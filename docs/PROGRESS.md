# Project Progress – AI Smart Home Hub

Date: 2025-09-11

This document summarizes the current state of the project after recent work to make trending discovery smarter and content generation monetization-ready.

Domain status: ai-smarthomehub.com configured as baseURL and live.

## What’s Implemented

- Multi‑source trending cache
  - Script `scripts/refresh_trending_keywords.py` aggregates Google Trends (if available), Reddit, YouTube, and Amazon (simulated if necessary) into `data/trending_keywords_cache.json` with graceful fallbacks and TTL cache directories created on demand.

- Daily lineup scheduler (2–4 topics/day, non‑duplicate)
  - `scripts/scheduler/select_daily_keywords.py` selects diverse topics, enforces a 14‑day cooldown (by normalized filename), and assigns an angle (best/alternatives/setup/troubleshooting/use‑case/vs).
  - Outputs: `data/daily_lineup_YYYYMMDD.json` and `data/daily_lineup_latest.json`.

- Non‑duplicate content with angle differentiation
  - `scripts/generate_quality_content_enhanced.py` now:
    - Accepts `angle` to generate different titles/sections/tags for the same keyword.
    - Injects dedicated sections for `setup`, `troubleshooting`, `alternatives`, `use‑case`, `vs`.
    - Adds a cross‑article similarity guard (5‑gram Jaccard vs. last 20 posts) with automatic angle fallback before accepting content.

- Keyword reuse filters
  - Daily and enhanced generators filter the last 30 days of articles to avoid repeating recent keywords.

- Scoring and multi‑source analyzer updates
  - Fixed trend scoring name collision by splitting into `*_from_series` and `*_from_keyword` with correct callsites.
  - Reddit/YouTube integrations activated (if secrets present), with simulated fallback on error or 401/429.

- Realtime workflow (enabled) with quality gate
  - `.github/workflows/realtime-trending-monitor.yml` created and enabled. Triggers `scripts/realtime_workflow.py` which calls the quality workflow to ensure only high‑quality content is published.
  - Added workflow concurrency groups for realtime and daily flows to prevent overlapping runs.

- Opportunity‑based gating in realtime trigger
  - Realtime selection now estimates an opportunity score (0–100) from v2 weights and includes it in gating alongside trend, urgency, search volume, and competition.

- Default daily volume and CI integration
  - Daily workflow default article_count set to 2 (configurable; clamped 2–4).
  - Daily flow refreshes trending cache then schedules the lineup before generation.

- Frontend critical patch (today)
  - Sticky navbar enforced in critical CSS to remain visible while scrolling (works even if main CSS loads late).
  - Featured image capped height/object-fit cover to avoid covering text on article pages.

## Verified Locally

- Ran `scripts/workflow_quality_enforcer.py --count 3 --pqs-mode` and generated 3 articles that passed quality gates (85–93% range, average ~90.5%).
- Verified lineup creation and trend cache refresh locally. Note: local secrets were not present, so Reddit/YouTube fell back to simulated data as designed.

## Known Issues / Notes

- Pytrends/urllib3 compatibility: some environments log `Retry.__init__() got an unexpected keyword argument 'method_whitelist'`. This is harmless due to fallback, but we should replace deprecated params with `allowed_methods` for best compatibility.
- Reddit 401: if Reddit secrets are missing/invalid, analyzer falls back to simulated data and logs warnings.
- Windows console encoding: we added stdout/stderr UTF‑8 wrappers in scripts that print Unicode icons to avoid GBK encode errors.
- Push via CLI requires valid local GitHub credentials (PAT/credential helper). Our local quick push failed due to missing credentials; CI will run after repo push.
- UX: Some users reported the navbar not visible on scroll and large featured images overlaying text. Critical CSS patch applied; further polishing planned.

## Artifacts Updated

- Workflows: `.github/workflows/daily-content-simple.yml`, `.github/workflows/realtime-trending-monitor.yml`
- Scripts: `scripts/refresh_trending_keywords.py`, `scripts/scheduler/select_daily_keywords.py`, `scripts/generate_quality_content_enhanced.py`, `scripts/generate_daily_content.py`
- Analyzer: `modules/keyword_tools/keyword_analyzer.py`
- Realtime trigger: `modules/trending/realtime_trigger.py`

## Next Steps (High‑level)

1. Strict lineup preference: make generators always use the daily lineup first (currently implemented for enhanced generator; confirm for all paths).
2. SimHash/MinHash fingerprint cache: persist per‑article fingerprints in `data/content_fingerprints.json` and use for faster, robust similarity checks.
3. Gating configuration: expose realtime thresholds entirely in `keyword_engine.yml` (opportunity, urgency, search, competition) and document tuning.
4. Google Search Console feedback loop: import query/impressions/clicks to boost high‑converting terms in scoring.
5. Amazon PA‑API integration (when approved): switch from simulated Amazon trends to live PA‑API signals and deepen monetization sections.
6. Replace pytrends deprecated params with `allowed_methods` and add lightweight rate limiting/rotating proxies if needed.
7. Unit tests for the scheduler, similarity guard, and gating functions.
8. Frontend modernization: local Tailwind build (no CDN), clamp reading width (720–800px), ensure TOC/anchors and sticky sidebar on desktop.

## Frontend Status (Today)

- Fixed overlay: removed global sticky header; article header forced non‑sticky; navbar fixed with high z‑index.
- Above‑the‑fold improved: moved featured image below header; tightened max‑height (desktop 300px, mobile 200px).
- Top ad slot: disabled via `config.yaml` until AdSense approval (`show_top_slot: false`).
- Newsletter inputs: unified white background/border/placeholder in homepage and footer forms.
- Body offset: added top padding to prevent fixed navbar covering content.

