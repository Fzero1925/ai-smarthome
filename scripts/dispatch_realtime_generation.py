#!/usr/bin/env python3
"""
Dispatch a realtime content generation workflow via GitHub repository_dispatch.

Usage:
  python scripts/dispatch_realtime_generation.py \
    --keyword "smart plug alexa" \
    --category smart_plugs \
    --angle best \
    --repo Fzero1925/ai-smarthome

Env:
  GITHUB_TOKEN: token with 'workflows:write' or repo dispatch permission.
  GITHUB_REPOSITORY (optional): defaults repo if --repo not provided.
"""
import os
import json
import argparse
import sys

import requests


def main():
    p = argparse.ArgumentParser(description='Send repository_dispatch for realtime content')
    p.add_argument('--keyword', required=True)
    p.add_argument('--category', default='general')
    p.add_argument('--angle', default='best')
    p.add_argument('--trend-score', type=float, default=0.8)
    p.add_argument('--reason', default='Manual dispatch')
    p.add_argument('--repo', default=os.getenv('GITHUB_REPOSITORY', ''))
    args = p.parse_args()

    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print('GITHUB_TOKEN not set', file=sys.stderr)
        return 2

    if not args.repo or '/' not in args.repo:
        print('Repository not specified. Use --repo owner/repo or set GITHUB_REPOSITORY.', file=sys.stderr)
        return 2

    payload = {
        'event_type': 'realtime_content_request',
        'client_payload': {
            'items': [{
                'keyword': args.keyword,
                'category': args.category,
                'angle': args.angle,
                'trend_score': args.trend_score,
                'reason': args.reason
            }]
        }
    }

    url = f'https://api.github.com/repos/{args.repo}/dispatches'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if r.status_code >= 300:
        print(f'Failed to dispatch: {r.status_code} {r.text}', file=sys.stderr)
        return 1
    print('Dispatch sent successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

