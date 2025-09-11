# Frontend TODO – AI Smart Home Hub

Updated: 2025-09-11

## High Priority (Stabilization)

- Chrome 140 review: verify no header/image overlays; confirm body top offset for fixed navbar across breakpoints.
- TL;DR placement: move after intro or collapse on mobile to keep first paragraph visible.
- Anchor offset: adjust in‑page anchors to account for fixed navbar.
- Normalize card image aspect ratios to prevent layout shifts.
- Unify global containers and spacing scale; remove duplicated inline CSS in templates.

## Medium Priority (Modernization)

- Local Tailwind build (no CDN) and extract utilities into main stylesheet.
- Sticky TOC on desktop: smooth anchors, correct offset, consistent typography scale.
- Form/Inputs/Buttons: consistent focus/hover/active states; A11y focus ring visible.

## Notes

- Top ad slot is disabled in `config.yaml` (`show_top_slot: false`) until AdSense approval and UX verification.
- Featured image capped (desktop 300px, mobile 200px) and moved below header to preserve above‑the‑fold readability.
