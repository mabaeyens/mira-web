# Backlog

## Done
- 2026-06-13 Remove TestFlight buttons (nav, hero, credits) — pending Apple external review; will restore once URL is approved
- 2026-06-13 Performance section: new #performance snap section between hero and screenshots with two animated horizontal bar charts (generation speed + prefill speed); 6th dot-nav entry; links to bench-results-2026-06-13.md in mira-core
- 2026-06-13 Fix carousel dot indicators: border was rendering on full padded tap-zone (44px ring) instead of 8px visual circle; moved border/fill to ::before pseudo-element
- 2026-06-06 Screenshot lightbox: tap/click any device frame to see current slide enlarged; Esc/backdrop closes; touch-action: pinch-zoom for native iOS zoom
- 2026-06-06 Magic Mouse carousel fix: replaced JS wheel handler with CSS scroll-snap (overflow-x: scroll + scroll-snap-type: x mandatory on each frame); browser handles Magic Mouse natively — zero JS in gesture path
- 2026-06-06 Fix iOS swipe: switched from pointer events to touchstart/touchmove/touchend; touchmove calls preventDefault when gesture is horizontal, blocking scroll-snap from stealing the touch
- 2026-06-06 Fix Magic Mouse wheel: gesture-lock model — fires once on first event, stays locked until 100ms of silence (gesture end); direction change allowed after 200ms (superseded by scroll-snap approach)
- 2026-06-06 Fix dark mode contrast for device tabs and screenshot captions (bumped from --dim to --muted)
- 2026-06-06 Fix iPad frame cropping: aspect-ratio corrected to 605/417 (iPad Pro 11" native 2420×1668); object-position: top (centered)
- 2026-06-06 Screenshots section: fixed-frame slider with 12 new screenshots (4 per device), device tabs (iPhone / Mac / iPad), inner image strip slides inside static frame, captions per slide, position dots, keyboard arrow key support

## Pending
- Restore TestFlight buttons once Apple external review approves the URL; add at nav, hero CTA, and credits (3 spots)
- Update performance section with remaining benchmark results when runs finish (omlx + Gemma4-26B gen/prefill); update --pct values proportionally if max changes
- Consider a waitlist CTA (Buttondown recommended for GDPR/EU) once TestFlight is live or as a pre-launch alternative
- Consider adding a visible swipe affordance / hint animation on mobile (first-visit only)

## Notes
- Performance chart data source: `mira-core/docs/bench-results-2026-06-13.md` (omlx 0.4.3, llama-bench tg512/pp1024, M5 32GB). omlx wins generation (55.7 t/s); ollama wins prefill (8,754 t/s pp1024) — both shown honestly. Prior bench runs not included: different omlx versions and methodology would introduce noise.
- Waitlist GDPR notes: site is at askmira.es (Spain, EU). Any email collection requires explicit opt-in, purpose disclosure, unsubscribe link, and a data processor agreement. Buttondown is EU-friendly with DPA available. Mailchimp/Brevo require heavier paperwork. Self-hosted gives full control but full responsibility.
- Dot nav tap targets: 44px button with ::before pseudo-element for the 8px visual circle. padding/margin hack was causing border to render at 44px instead of 8px.
- Magic Mouse carousel: all JS-based approaches (cooldown, gesture-lock, direction-change guard) fail because JS can't reliably distinguish intentional swipes from momentum. CSS scroll-snap is the correct solution — the browser uses OS gesture APIs that JS cannot access.
- Nested scroll-snap: outer container scroll-snap-type: y mandatory + inner frames scroll-snap-type: x mandatory works in modern Safari. touch-action: pan-x on frames lets vertical page swipes propagate to outer container.
- iOS Safari inside a scroll-snap container ignores touch-action: pan-y in some cases; explicit touchmove + preventDefault on horizontal gestures is required (JS handler approach, now superseded by native scroll on the frames)
- iPad Pro 11" screenshots are 2420×1668 (ratio 605:417 ≈ 1.45:1) — not 4:3; frame must match or images clip on the right
- Device tab and caption text: --dim (#57534E in dark mode) is near-invisible; --muted (#A8A29E in dark mode) is the correct token
- GitHub Pages CDN can take 1–3 min to propagate after push; private window bypasses local cache but not CDN
