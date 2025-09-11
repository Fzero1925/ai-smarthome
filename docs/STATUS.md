# Project Status – AI Smart Home Hub

Updated: 2025-09-11 22:45

- Domain: ai-smarthomehub.com (configured as baseURL)
- Current: Application prep phase — fix UX and duplication first

## AdSense & Amazon Timing

- Recommendation: Apply in 3–7 days after:
  - Frontend UX fixed (sticky navbar visible while scrolling; featured images no longer cover text; stable reading width)
  - Duplicate content risk reduced (similarity guard tightened; fingerprint cache online or stricter PQS threshold as interim)
  - Pages and policies verified (About/Privacy/Contact, internal links)
  - Core Web Vitals checked (CLS < 0.1, LCP < 2.5s)

- If applying now: Pass risk is moderate due to UX and duplication feedback; waiting a few days with fixes improves odds significantly.

## Daily Generation Settings (proposed)

- Volume: 2–4 articles/day for the next 3–7 days
- Quality gate: PQS minimum 0.88–0.90
- Lineup-first: Every generator path consumes `data/daily_lineup_YYYYMMDD.json`
- Similarity: Guard threshold set to 0.30 (cosine) over 90 days; this treats ≥30%为重复。后续内容库扩大可适度放宽（如0.35–0.4），但不建议超过0.5。
  - SimHash precheck: 64‑bit Hamming ≤ 12 considered near‑duplicate.
  - Section‑level check: run if doc‑level passes; sections ≥200 words flagged when TF‑IDF ≥ 0.45.
  - Config: `config/uniqueness.yml` controls thresholds, window, excluded headings.
- Realtime: Keep enabled; skip if daily target met or gates fail

## Frontend Plan

- Hotfix (applied):
  - Sticky navbar enforced in `static/css/critical.css` (works even if `main.css` delays)
  - Featured images capped height and object-fit cover to prevent overlaying content

- Short-term (today–tomorrow):
  - Clamp reading width to 720–800px for articles
  - Ensure TOC placement does not push content below the fold
  - Verify z-index layering; navbar above any hero/featured media

- Modernization (this week):
  - Local Tailwind build (no CDN) and extract utility classes
  - Audit templates for consistent containers, spacing, and image aspect ratios
  - Add sticky sidebar TOC on desktop, smooth anchors, and improved typography scale

## Docs & Repo Hygiene

- Canonical docs: `docs/PROGRESS.md`, `docs/TODO.md`, and this `docs/STATUS.md`
- Archive: move outdated progress summaries to `oldfile/`
- Tests: keep all test assets in `test/`
- Git ignore: `oldfile/` and `test/` already excluded in `.gitignore`
