# Setup & Workflows

## Secrets / Environment

Add these to GitHub → Repository Settings → Secrets and variables → Actions:

- Reddit: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`
- YouTube: `YOUTUBE_API_KEY`
- Telegram (optional): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Amazon PA‑API (later): `AMAZON_PAAPI_ACCESS_KEY`, `AMAZON_PAAPI_SECRET_KEY`, `AMAZON_AFFILIATE_TAG`

## CI Workflows

- Daily Content: `.github/workflows/daily-content-simple.yml`
  - Steps: refresh trending cache → select daily lineup → generate (quality gate) → commit
  - Default `article_count`: 3 (override via workflow dispatch)
  - Concurrency group: `daily-content`

- Realtime Trending: `.github/workflows/realtime-trending-monitor.yml`
  - Schedule: every 30 minutes (UTC 6–22), and manual dispatch
  - Triggers generation only if gating thresholds are met
  - Concurrency group: `realtime-trending`

## Local Commands

- Refresh trends cache
  - `python scripts/refresh_trending_keywords.py`
- Select lineup (2–4 topics)
  - `python scripts/scheduler/select_daily_keywords.py --count 3`
- Quality‑gated generation (PQS v3 strict mode)
  - `python scripts/workflow_quality_enforcer.py --count 3 --pqs-mode`

## Troubleshooting

- Pytrends/urllib3 deprecations: fallback preserves functionality; planned fix is to move from `method_whitelist` to `allowed_methods`.
- Missing Reddit/YouTube keys: analyzer falls back to simulated data; logs warnings.
- Local Git push requires credentials: use `scripts/quick_commit_push.py` or configure PAT/credential helper.

