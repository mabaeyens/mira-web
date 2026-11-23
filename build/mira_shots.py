#!/usr/bin/env python3
"""Convert the Mira website screenshots (mira-apps/AppStore/website) to WebP in assets/shots/mira.
iPhone -> 960 wide, iPad -> 1600, Mac -> 2000. The iPad PNGs carry a stale EXIF orientation tag
while their pixels are already upright, so the metadata is stripped first."""
import os, subprocess, tempfile
SRC = os.path.expanduser("~/Projects/mira-apps/AppStore/website")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets/shots/mira")
SETS = {"iphone": 960, "ipad-landscape": 1600, "macos": 2000}
NAME = {"iphone": "iphone", "ipad-landscape": "ipad", "macos": "mac"}
for dev, w in SETS.items():
    for mode in ("light", "dark"):
        d = os.path.join(SRC, f"{dev}-{mode}")
        for f in sorted(os.listdir(d)):
            if not f.endswith(".png"): continue
            out = os.path.join(OUT, f"{NAME[dev]}-{mode}-{f[:-4]}.webp")
            with tempfile.TemporaryDirectory() as t:
                tmp = os.path.join(t, "s.png")
                subprocess.run(["magick", os.path.join(d, f), "-strip", "-resize", f"{w}x", tmp], check=True)
                subprocess.run(["cwebp", "-quiet", "-q", "82", tmp, "-o", out], check=True)
            print(out, os.path.getsize(out) // 1024, "KB")
