# Backlog

## Done
- [2026-06-14] Fixed mobile/tablet rendering. Replaced the runtime Tailwind **CDN** (`cdn.tailwindcss.com`) with a **vendored, purged** `assets/tailwind.css` so layout no longer depends on a third-party script — it was collapsing to a bare logo on iPad under a content blocker / Lockdown Mode. Also made the layout responsive: natural document scroll on mobile (scroll-snap kept desktop-only), wrapping meta rows, dot-nav hidden on phones, icon-only nav chips on narrow screens, and `img { max-width:100% }` overflow guards.
- [2026-06-14] Promoted the "field-manual" redesign to the live site (`index.html`; old design kept in git history). Scroll-snap field-manual layout, containment hairline frame, numbered section labels (`01 /`…), capability index numerals, LinkedIn links in nav + footer, and a rebuilt hero.
- [2026-06-14] Hero "local generation" panel now replays four **real** Mira conversations as an auto-scrolling chat, mirroring the app UI: extended **thinking** (Thinking…→Thought), **web sources** (Pages read), **RAG** (Document sections used + scores), and **code** (language label + Copy). Live tok/s readout; `prefers-reduced-motion` renders a single static scene.

## Pending
- Browser QA of the new live design: scene pacing/legibility, hero panel fits within 100vh without clipping, mobile stacking (text over panel), dark/light across thinking/sources/RAG/code, reduced-motion path.
- Restore TestFlight buttons once Apple external review approves the URL; add back at nav, hero CTA, and credits (3 spots)
- Consider a waitlist CTA (Buttondown recommended for GDPR/EU) once TestFlight is live or as a pre-launch alternative

## Notes
- Design direction is deliberately "field manual for a machine you own" (mono/spec-sheet, warm stone + terracotta, honest copy) — chosen over a generic Raycast/Arc/Linear SaaS template to stay distinctive.
- Hero demo content is pulled **verbatim (trimmed)** from real conversations in `~/.local/share/mira/conversations.db` (non-sensitive: black holes, Madrid weather via aemet.es, Apple Silicon brief summary, palindrome). Only the RAG source-chip scores/snippets are representative — Mira doesn't persist retrieved chunks; prompts/thinking/answers are real. Personal/Vera conversations were deliberately avoided.
- Mira's SwiftUI app palette is identical to the site's CSS `:root` tokens (bg `#1C1917`, accent `#D09268`, muted `#A8A29E`, surface `#232120`, border `#57534E`), so the existing tokens reproduce the app's look — no new colors needed.
- CSS: page-specific component CSS/JS still lives inline in `index.html`; shared structural CSS is in `style.css`. Tailwind utilities are compiled to `assets/tailwind.css` (committed). **Rebuild after changing any Tailwind class in the markup:** `npx tailwindcss@3 -c tailwind.config.js -i tailwind-input.css -o assets/tailwind.css --minify` (config in `tailwind.config.js`, input in `tailwind-input.css`). No CDN at runtime.
