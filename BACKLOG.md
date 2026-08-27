# Backlog

## Pending

- **Aura Android — swap in a real Google Play badge** once the public listing URL exists. Every Android CTA currently says "coming to Google Play" and links the `aura-android` GitHub repo; the Play listing is still internal-testing / Spanish-only (`com.mab.Aura`). When public, add a "Get it on Google Play" badge across hero/footer/Android card and the Support "Is Aura on Android?" FAQ.
- **Aura Android — capture an annotated AEMET-key guide** so Support has a real Android walkthrough (gear → Ajustes → AEMET key), matching the iPhone one. Only a text note exists today.
- **Aura CPP — art generation (the last parked piece).** The four pages are live on ASC with promo text + a keyword plan; what's parked is the screenshots. GPT Image 2 generates only the text-free living-sky backgrounds (6 tuned prompts); real screenshots + headlines are composited by code. Locked to planning only until I say go (cost is real); EN+ES adds no extra generations. Full detail in the gitignored `notes/aura-custom-product-page.md`; keyword follow-up tracked in aura-apps.
- **Vera — screenshots + `og.png`** (spec `specs/02`). `vera/index.html` still has the `TODO(assets)` marker and `vera/assets/og.png` doesn't exist yet (social cards show a broken image). Needs assets, then wire in a simple `.mac-shadow` image row.
- **Vera — migrate `vera/privacy/index.html` to the shared `style.css`**, then delete the Tailwind files (`assets/tailwind.css`, `tailwind.config.js`, `tailwind-input.css`). That page is the last thing still linking Tailwind.
- **Browser QA of the live design** — scene pacing/legibility, hero panel fits within 100vh, mobile stacking, dark/light across thinking/sources/RAG/code, reduced-motion path.
- **Restore TestFlight buttons** (nav, hero CTA, credits) once Apple external review approves the URL; consider a waitlist CTA (Buttondown, GDPR-friendly) as a pre-launch alternative.

## Done (one-liners; full detail in git history)

- [2026-08-27] Aura site aligned with Google Play Misleading Claims policy: removed superiority claims, added open-data source links + non-official disclaimer on all four `aura/` pages, synced EN hero with Android copy (0bbf12d).
- [2026-08-26] Reframed the whole `/aura` site from Apple-only to iOS + Android (new `aura-android` repo): Android named across hero/copy/meta/footer, "Now on Android" card + 5-shot Android gallery, platform-accurate privacy card, "coming to Google Play" (no badge yet), Play data-safety + GDPR-rights sections in Privacy, Android FAQs + copy-email button in Support.
- [2026-08-24] Aura App Store custom product pages: 4 CPPs live on ASC (Widgets, Avisos CAP, Apple Watch, Datos AEMET) with promo text; CPP mockup shipped as a real page at `/aura/cpp`; widget board sized by real grid footprint; gallery refreshed from ASC materials (colour-only widgets); added the gitignored `notes/` folder. Keyword work handed to aura-apps' next release.
- [2026-08-24] Aura Soporte: AEMET-key request button + real opendata link; Privacidad: corrected UV source to Open-Meteo/CAMS and added a "what actually leaves your device" payload snippet (f6c92a0).
- [2026-08-23] Aura support page at `/aura/soporte` (fixes App Store Guideline 1.5): bilingual EN/ES, contact email + 8-item FAQ, language toggle remembered in localStorage (34b4b8f, f025cc5, 6f719bd).
- [2026-08-22] Aura page: real screenshots + gallery (scroll-snap rails per device), dropped Mac as a surface, copy pulled up to shipped v1.0.0; added `og.png`.
- [2026-08-20] Added the `/aura` subpage (sky-blue accent, shared Mira design system, AEMET OpenData positioning).
- [2026-07-10] Full site redesign (hybrid Apple-clean / field-manual): rewrote `index.html` + `style.css`, dropped Tailwind from `/` and `/vera`, natural scroll, live-demo hero; rebuilt `/vera` on the shared design system (teal), added Download for Mac + View source (vera-apps now public/MIT), added the previously-untracked `/vera/privacy`.
- [2026-06-22] Added the `/vera` subpage (teal accent, TestFlight beta CTA).
- [2026-06-14] Promoted the "field-manual" redesign live; replaced the Tailwind CDN with a vendored/purged `assets/tailwind.css`; responsive mobile/tablet fixes; hero panel replays four real Mira conversations (thinking / sources / RAG / code, live tok/s, reduced-motion safe).

## Notes

- Design direction is deliberately "field manual for a machine you own" (mono/spec-sheet, warm stone + terracotta, honest copy), chosen over a generic SaaS template to stay distinctive.
- Hero demo content is pulled verbatim (trimmed) from real non-sensitive conversations in `~/.local/share/mira/conversations.db` (black holes, Madrid weather, Apple Silicon brief, palindrome). Only the RAG source-chip scores/snippets are representative; prompts/thinking/answers are real.
- Mira's SwiftUI app palette matches the site's CSS `:root` tokens (bg `#1C1917`, accent `#D09268`, muted `#A8A29E`, surface `#232120`, border `#57534E`), so no new colors are needed.
- Page-specific component CSS/JS lives inline in `index.html`; shared structural CSS is in `style.css`. Tailwind utilities are compiled to `assets/tailwind.css` (committed, still used by `vera/privacy`). Rebuild after any Tailwind class change: `npx tailwindcss@3 -c tailwind.config.js -i tailwind-input.css -o assets/tailwind.css --minify`.
