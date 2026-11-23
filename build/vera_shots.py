#!/usr/bin/env python3
"""Convert the Vera website screenshots (vera-apps/AppStore/website) to WebP in assets/shots/vera.
iPad 2752x2064 -> 1600 wide, iPhone 1320x2868 -> 640 wide. Keeps the 01..05 numbering."""
import os, subprocess
SRC = os.path.expanduser("~/Projects/vera-apps/AppStore/website")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets/shots/vera")
SETS = {"ipad-landscape-light": ("ipad-light", 1600), "ipad-landscape-dark": ("ipad-dark", 1600), "iphone-light": ("iphone", 640)}
for folder, (prefix, w) in SETS.items():
    for f in sorted(os.listdir(os.path.join(SRC, folder))):
        if not f.endswith(".png"): continue
        slug = f.split("-", 2)[2] if f.startswith(("landscape-")) else f.split("-", 1)[1]
        n = slug[:-4]
        out = os.path.join(OUT, f"{prefix}-{n}.webp")
        subprocess.run(["cwebp", "-q", "82", "-resize", str(w), "0", os.path.join(SRC, folder, f), "-o", out], check=True, capture_output=True)
        print(out, os.path.getsize(out) // 1024, "KB")
