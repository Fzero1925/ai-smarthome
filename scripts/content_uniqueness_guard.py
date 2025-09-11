#!/usr/bin/env python3
"""
Content Uniqueness Guard

Checks a target Markdown article against recent articles for near-duplicate content
using TF‑IDF cosine similarity. Exits non‑zero if similarity exceeds threshold.

Usage:
  python scripts/content_uniqueness_guard.py --target content/articles/foo.md --threshold 0.85 --days 30
"""
import os
import re
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def strip_front_matter(text: str) -> str:
    # Remove YAML front matter and code fences
    text = re.sub(r"^---[\s\S]*?---\s+", "", text, flags=re.M)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_recent_articles(dir_path: str, days: int = 30) -> List[str]:
    docs = []
    if not os.path.exists(dir_path):
        return docs
    cutoff = datetime.now() - timedelta(days=days)
    for name in os.listdir(dir_path):
        if not name.endswith('.md'):
            continue
        path = os.path.join(dir_path, name)
        try:
            ts = datetime.fromtimestamp(os.path.getctime(path))
        except Exception:
            continue
        if ts < cutoff:
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                docs.append(strip_front_matter(f.read()))
        except Exception:
            continue
    return docs


def check_uniqueness(target_path: str, pool_dir: str, days: int, threshold: float) -> float:
    with open(target_path, 'r', encoding='utf-8') as f:
        target_text = strip_front_matter(f.read())
    pool = load_recent_articles(pool_dir, days)
    if not pool:
        return 0.0
    corpus = pool + [target_text]
    vec = TfidfVectorizer(stop_words='english', max_df=0.9)
    X = vec.fit_transform(corpus)
    sims = cosine_similarity(X[-1], X[:-1]).flatten()
    return float(sims.max()) if sims.size else 0.0


def main():
    p = argparse.ArgumentParser(description='Check article uniqueness against recent posts')
    p.add_argument('--target', required=True, help='Path to target Markdown file')
    p.add_argument('--pool', default='content/articles', help='Directory of existing articles')
    p.add_argument('--days', type=int, default=30, help='Lookback window in days')
    p.add_argument('--threshold', type=float, default=0.85, help='Max allowed cosine similarity (0-1)')
    args = p.parse_args()

    if not os.path.exists(args.target):
        print(f"Target not found: {args.target}")
        return 2

    sim = check_uniqueness(args.target, args.pool, args.days, args.threshold)
    print(json.dumps({'max_similarity': round(sim, 4), 'threshold': args.threshold}))
    if sim >= args.threshold:
        print(f"Too similar: {sim:.3f} >= {args.threshold:.2f}")
        return 3
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

