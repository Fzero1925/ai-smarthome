# TODO Backlog – AI Smart Home Hub

Last updated: 2025-09-11 (post-domain + frontend fixes)

## Now (High Priority)

- [ ] Lineup first policy – ensure every generator path consumes `data/daily_lineup_YYYYMMDD.json` before any fallback; document precedence.
- [ ] Realtime thresholds in config – move all gating thresholds to `keyword_engine.yml` and log matched/failed checks cleanly.
- [ ] Pytrends compat – replace deprecated `method_whitelist` with `allowed_methods`; add small retry/backoff and optional proxy support.
- [ ] Fingerprint cache – implement SimHash/MinHash persistence in `data/content_fingerprints.json` and use it in similarity guard.
- [ ] Frontend critical fixes – sticky navbar across pages via `static/css/critical.css`, cap featured image height and ensure text visibility on article pages.
- [ ] Content duplication guard – set daily volume to 2–4 and enforce cosine similarity guard at 0.30 over 90 days (treat ≥30% as duplicate); PQS min threshold 88–90 until fingerprint cache ships.
  - Add SimHash precheck (64‑bit Hamming ≤ 12), maintain `data/content_fingerprints.json` via workflows.
  - Add section‑level TF‑IDF (≥200 words) with threshold 0.45; exclude boilerplate sections via `config/uniqueness.yml`.

## Next (Medium Priority)

- [ ] Search Console ingestion – weekly import of queries/impressions/clicks per URL; feed into scoring (opportunity boost).
- [ ] Angle diversification heuristics – smarter angle selection by keyword intent (e.g., product vs. how‑to vs. comparison).
- [ ] Realtime concurrency tuning – ensure only one realtime cycle generates at a time; skip if daily already met target.
- [ ] Expand lineup diversity – enforce category caps per day (e.g., max 1 per category unless inventory low).
- [ ] Frontend modernization – consolidate Tailwind via local build (no CDN), extract CSS into partials, add reading width clamp (720–800px), TOC sticky sidebar on desktop.

## Later (Monetization & Polishing)

- [ ] Amazon PA‑API – integrate live bestseller/price signals; add affiliate blocks with price ranges and CTA components.
- [ ] Evidence seeding – expand `config/evidence_seeder.json` with stronger external references per category.
- [ ] Internal links pass – run `scripts/seo/optimize_internal_links.py` post‑publish in workflows.
- [ ] Structured data – add ItemList/FAQ JSON‑LD injection in generators with validation snippets.
- [ ] Add minimal unit tests – scheduler, similarity guard, gating, analyzer fallbacks.
- [ ] AdSense readiness checklist – navigation, CLS < 0.1, LCP < 2.5s, About/Privacy/Contact, unique content ratio > 90% over last 20 posts.

## Ops / DX

- [ ] Credentials checklist – README section for REDDIT_*, YOUTUBE_API_KEY, TELEGRAM_* with quick diagnostics.
- [ ] CI badges – add workflow status badges to README.
- [ ] Sample .env – include `.env.example` mapping all env variables.
- [ ] Docs hygiene – move outdated progress/summary docs to `oldfile/`; keep `docs/PROGRESS.md` and `docs/TODO.md` canonical.

