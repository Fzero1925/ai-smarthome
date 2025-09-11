#!/usr/bin/env python3
"""
Image Selector: picks the best featured_image for articles using local library.

- Scans static/images/products/<category>, products/general, scenes
- Scores candidates by keyword/category/scene/quality + usage penalty
- Writes featured_image, featured_image_alt/title back to front matter

Usage:
  python scripts/image_selector.py --target content/articles/foo.md [--dry-run]
  python scripts/image_selector.py --articles-dir content/articles [--dry-run]
"""
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

import frontmatter  # python-frontmatter
from PIL import Image
import yaml


ROOT = Path(__file__).resolve().parents[1]
STATIC_IMAGES = ROOT / "static" / "images"
USAGE_FILE = ROOT / "data" / "image_usage.json"
IMAGE_CONFIG = ROOT / "image_config.yml"
MAPPINGS_FILE = ROOT / "config" / "image_mappings.yml"


def load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_json(p: Path, data: dict):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def norm_tokens(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9]+", (text or "").lower())
    return words


def apply_aliases(tokens: List[str], mappings: dict) -> List[str]:
    brand_alias = mappings.get("brands", [])
    alias_map = {}
    for b in brand_alias:
        name = b.get("name", "").lower()
        alias_map[name] = name
        for a in b.get("aliases", []):
            alias_map[a.lower()] = name
    out = []
    for t in tokens:
        out.append(alias_map.get(t, t))
    return out


def get_category(article: dict) -> str:
    cats = article.get("categories") or article.get("category") or []
    if isinstance(cats, list) and cats:
        return str(cats[0]).strip().lower()
    if isinstance(cats, str) and cats:
        return cats.strip().lower()
    return "general"


def collect_candidates(category: str) -> List[Path]:
    paths = []
    # category dir
    cat_dir = STATIC_IMAGES / "products" / category
    if cat_dir.exists():
        paths.extend([p for p in cat_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
    # general
    gen_dir = STATIC_IMAGES / "products" / "general"
    if gen_dir.exists():
        paths.extend([p for p in gen_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
    # scenes
    sc_dir = STATIC_IMAGES / "scenes"
    if sc_dir.exists():
        paths.extend([p for p in sc_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
    # fallback default
    def_img = STATIC_IMAGES / "default-article.jpg"
    if def_img.exists():
        paths.append(def_img)
    return paths


def score_image(p: Path, tokens: List[str], category: str, cfg: dict, usage: dict, mappings: dict) -> float:
    try:
        with Image.open(p) as im:
            w, h = im.size
    except Exception:
        w = h = 0

    q = cfg.get("quality", {})
    rules = cfg.get("quality_rules", {})
    scoring = cfg.get("scoring", {})
    scenes = cfg.get("scenes", {})

    base = 0.0
    # keyword match
    name_tokens = norm_tokens(p.stem)
    overlap = len(set(tokens) & set(name_tokens))
    base += scoring.get("keyword_match_weight", 0.4) * (overlap / max(1, len(tokens)))

    # category match
    in_cat = ("products" in p.parts and category in [x.lower() for x in p.parts])
    base += scoring.get("category_match_weight", 0.3) * (1.0 if in_cat else 0.0)

    # scene relevance
    scene_score = 0.0
    for scene, val in scenes.items():
        if scene in p.stem.lower():
            scene_score = max(scene_score, float(val))
    base += scoring.get("scene_relevance_weight", 0.2) * scene_score

    # quality bonus
    qw = q.get("min_width", 800)
    qh = q.get("min_height", 600)
    quality_ok = 1.0 if (w >= qw and h >= qh) else 0.0
    base += scoring.get("quality_bonus_weight", 0.1) * quality_ok

    # usage penalty
    usage_count = usage.get(str(p).replace(str(ROOT), ""), 0)
    penalty_factor = scoring.get("usage_penalty_factor", 0.5)
    max_penalty = scoring.get("max_usage_penalty", 2.0)
    base -= min(max_penalty, usage_count * penalty_factor) * 0.05  # small step penalty

    return base


def pick_featured(article_path: Path, dry_run=False) -> Tuple[bool, str]:
    cfg = load_yaml(IMAGE_CONFIG)
    mappings = load_yaml(MAPPINGS_FILE)
    usage = load_json(USAGE_FILE)

    post = frontmatter.load(article_path)
    fm = post.metadata or {}
    category = get_category(fm)

    text_for_tokens = " ".join([
        str(fm.get("title", "")),
        " ".join(fm.get("tags", []) if isinstance(fm.get("tags"), list) else []),
        str(fm.get("product_review", {}).get("name", "")),
        str(fm.get("product_review", {}).get("brand", "")),
        article_path.stem
    ])
    tokens = norm_tokens(text_for_tokens)
    tokens = apply_aliases(tokens, mappings)

    candidates = collect_candidates(category)
    scored = []
    for p in candidates:
        s = score_image(p, tokens, category, cfg, usage, mappings)
        scored.append((s, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    min_score = cfg.get("quality_rules", {}).get("min_image_relevance_score", 0.6)
    chosen = None
    for s, p in scored:
        if s >= min_score:
            chosen = p
            break
    if not chosen and scored:
        chosen = scored[0][1]

    if not chosen:
        return False, "no_candidate"

    # Compose fields
    rel_path = "/" + str(chosen.relative_to(ROOT)).replace("\\", "/")
    alt_tpl = cfg.get("seo", {}).get("alt_templates", {}).get("hero", "{category} product overview")
    alt = alt_tpl.format(category=category.replace("-", " "), keyword=fm.get("title", "")).strip()
    alt = re.sub(r"\s+", " ", alt)[:125]

    # Write back
    fm["featured_image"] = rel_path
    fm["featured_image_alt"] = alt
    fm["featured_image_title"] = fm.get("title", "")
    post.metadata = fm

    if not dry_run:
        with article_path.open("w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        # update usage
        key = rel_path
        usage[key] = usage.get(key, 0) + 1
        save_json(USAGE_FILE, usage)
    return True, rel_path


def main():
    ap = argparse.ArgumentParser(description="Select and set featured images for articles")
    ap.add_argument("--target", help="single article path")
    ap.add_argument("--articles-dir", default="content/articles", help="directory for batch")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.target:
        ok, msg = pick_featured(Path(args.target), dry_run=args.dry_run)
        print(json.dumps({"success": ok, "message": msg}))
        return 0 if ok else 1

    # batch
    dirp = Path(args.articles_dir)
    files = sorted([p for p in dirp.glob("*.md")])
    updated = 0
    for p in files:
        ok, _ = pick_featured(p, dry_run=args.dry_run)
        if ok:
            updated += 1
    print(json.dumps({"updated": updated, "total": len(files)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

