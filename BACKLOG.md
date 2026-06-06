# Backlog

## Done
- 2026-06-06 Fix iOS swipe: switched from pointer events to touchstart/touchmove/touchend; touchmove calls preventDefault when gesture is horizontal, blocking scroll-snap from stealing the touch
- 2026-06-06 Fix Magic Mouse wheel: gesture-lock model — fires once on first event, stays locked until 100ms of silence (gesture end); direction change allowed after 200ms
- 2026-06-06 Fix dark mode contrast for device tabs and screenshot captions (bumped from --dim to --muted)
- 2026-06-06 Fix iPad frame cropping: aspect-ratio corrected to 605/417 (iPad Pro 11" native 2420×1668); object-position: top (centered)
- 2026-06-06 Screenshots section: fixed-frame slider with 12 new screenshots (4 per device), device tabs (iPhone / Mac / iPad), inner image strip slides inside static frame, captions per slide, position dots, keyboard arrow key support

## Pending
- Consider adding a visible swipe affordance / hint animation on mobile (first-visit only)

## Notes
- Magic Mouse generates wheel momentum events for up to 1.5–2s after a fast flick — time-gap approaches (200ms, 600ms) all failed; gesture-lock with silence-based unlock is the correct pattern
- iOS Safari inside a scroll-snap container ignores touch-action: pan-y in some cases; explicit touchmove + preventDefault on horizontal gestures is required
- iPad Pro 11" screenshots are 2420×1668 (ratio 605:417 ≈ 1.45:1) — not 4:3; frame must match or images clip on the right
- Device tab and caption text: --dim (#57534E in dark mode) is near-invisible; --muted (#A8A29E in dark mode) is the correct token
- GitHub Pages CDN can take 1–3 min to propagate after push; private window bypasses local cache but not CDN
