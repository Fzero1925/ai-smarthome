# TODO Backlog – AI Smart Home Hub

Last updated: 2025-09-11

## Now (High Priority)

- [ ] Lineup first policy – ensure every generator path consumes `data/daily_lineup_YYYYMMDD.json` before any fallback; document precedence.
- [ ] Realtime thresholds in config – move all gating thresholds to `keyword_engine.yml` and log matched/failed checks cleanly.
- [ ] Pytrends compat – replace deprecated `method_whitelist` with `allowed_methods`; add small retry/backoff and optional proxy support.
- [ ] Fingerprint cache – implement SimHash/MinHash persistence in `data/content_fingerprints.json` and use it in similarity guard.

## Next (Medium Priority)

- [ ] Search Console ingestion – weekly import of queries/impressions/clicks per URL; feed into scoring (opportunity boost).
- [ ] Angle diversification heuristics – smarter angle selection by keyword intent (e.g., product vs. how‑to vs. comparison).
- [ ] Realtime concurrency tuning – ensure only one realtime cycle generates at a time; skip if daily already met target.
- [ ] Expand lineup diversity – enforce category caps per day (e.g., max 1 per category unless inventory low).

## Later (Monetization & Polishing)

- [ ] Amazon PA‑API – integrate live bestseller/price signals; add affiliate blocks with price ranges and CTA components.
- [ ] Evidence seeding – expand `config/evidence_seeder.json` with stronger external references per category.
- [ ] Internal links pass – run `scripts/seo/optimize_internal_links.py` post‑publish in workflows.
- [ ] Structured data – add ItemList/FAQ JSON‑LD injection in generators with validation snippets.
- [ ] Add minimal unit tests – scheduler, similarity guard, gating, analyzer fallbacks.

## Ops / DX

- [ ] Credentials checklist – README section for REDDIT_*, YOUTUBE_API_KEY, TELEGRAM_* with quick diagnostics.
- [ ] CI badges – add workflow status badges to README.
- [ ] Sample .env – include `.env.example` mapping all env variables.

