#!/usr/bin/env python3
"""
Ensure all recent articles have a valid, keyword-relevant featured_image.
Uses the existing ArticleImageUpdater without forcing changes if already set.

Usage:
  python scripts/fix_featured_images.py [--force]
"""
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Fix featured images for articles')
    parser.add_argument('--articles-dir', default='content/articles')
    parser.add_argument('--force', action='store_true', help='Force update even if present')
    args = parser.parse_args()

    # Lazy import to avoid encoding issues in Windows shell
    from update_article_images import ArticleImageUpdater  # type: ignore

    updater = ArticleImageUpdater(args.articles_dir)
    res = updater.batch_update_articles(force_update=args.force)
    return 0 if res.get('success') else 1


if __name__ == '__main__':
    raise SystemExit(main())

