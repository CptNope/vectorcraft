#!/usr/bin/env python3
"""Add PWA features to the VectorCraft Trunk build, preserving the upstream UI.

The generated site is valid under a GitHub Pages /repository/ prefix.
This file uses only the Python standard library, including for its icons.
"""
from __future__ import annotations

import math
import os
import shutil
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def make_png(path: Path, n: int) -> None:
    """Draw a generic editable-path icon, not an upstream trademark."""
    segments = [((.21, .70), (.35, .35)), ((.35, .35), (.53, .63)),
                ((.53, .63), (.73, .27)), ((.73, .27), (.82, .48))]
    points = [(.21,.70), (.35,.35), (.53,.63), (.73,.27), (.82,.48)]
    raw = bytearray()
    def segment_distance(px, py, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx-ax, by-ay
        t = max(0., min(1., ((px-ax)*dx + (py-ay)*dy)/(dx*dx+dy*dy)))
        return math.hypot(px-(ax+t*dx), py-(ay+t*dy))
    for y in range(n):
        raw.append(0)  # PNG filter type 0
        for x in range(n):
            px, py = (x+.5)/n, (y+.5)/n
            r, g, b = 16, 24, 39
            if .08 < px < .92 and .08 < py < .92:
                r, g, b = 26, 47, 70
            if min(segment_distance(px, py, a, b) for a,b in segments) < .014:
                r, g, b = 85, 215, 230
            if min(math.hypot(px-a, py-b) for a,b in points) < .027:
                r, g, b = 244, 250, 255
            raw.extend((r,g,b,255))
    def chunk(tag, data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB",n,n,8,6,0,0,0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw),9))
    png += chunk(b"IEND",b"")
    path.write_bytes(png)

def main(site: Path) -> None:
    index = site/"index.html"
    if not index.is_file():
        raise SystemExit(f"Expected a compiled Trunk index at {index}")
    icons = site/"icons"
    icons.mkdir(parents=True,exist_ok=True)
    for name, size in (("icon-192.png",192),("icon-512.png",512),("apple-touch-icon.png",180)):
        make_png(icons/name,size)

    for name in ("manifest.webmanifest","sw.js"):
        shutil.copy2(ROOT/"pwa"/name,site/name)
    for name in ("NOTICE","LICENSE-MIT","LICENSE-APACHE","ASSETS.md"):
        source=ROOT/name
        if source.exists():
            shutil.copy2(source,site/name)
    (site/".nojekyll").touch()

    html=index.read_text(encoding="utf-8")
    header="""\
<link rel="manifest" href="./manifest.webmanifest">
<meta name="theme-color" content="#101827">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="./icons/apple-touch-icon.png">
"""
    registration="""\
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () =>
    navigator.serviceWorker.register('./sw.js')
      .catch(error => console.warn('PWA registration failed', error)));
}
</script>
"""
    if 'rel="manifest"' not in html:
        if "</head>" not in html:
            raise SystemExit("Missing </head> tag in Trunk output")
        html=html.replace("</head>",header+"</head>",1)
    if "navigator.serviceWorker.register('./sw.js')" not in html:
        if "</body>" not in html:
            raise SystemExit("Missing </body> tag in Trunk output")
        html=html.replace("</body>",registration+"</body>",1)
    index.write_text(html,encoding="utf-8")
    # Each release gets its own cache to avoid stale editor WASM on upgrades.
    version=(os.getenv("GITHUB_SHA") or "local")[:12]
    worker=(site/"sw.js")
    worker.write_text(worker.read_text(encoding="utf-8").replace("__BUILD_VERSION__", version), encoding="utf-8")
    for name in ("index.html","manifest.webmanifest","sw.js",
                 "icons/icon-192.png","icons/icon-512.png"):
        if not (site/name).is_file():
            raise SystemExit("Missing PWA output "+name)
    print(f"Prepared GitHub Pages PWA: {site}")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python3 pwa/prepare_site.py dist/web")
    main(Path(sys.argv[1]).resolve())
