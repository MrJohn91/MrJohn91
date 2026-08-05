#!/usr/bin/env python3
"""Convert a prepped grayscale image into a monochrome ASCII SVG."""
import sys
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "mrj-ascii.svg"

# Dense-to-sparse ramp, darkest first.
RAMP = "@%#*+=-:. "

CELL_W = 6.2
CELL_H = 11.5
FONT_SIZE = 12


def pixel_to_char(v: int) -> str:
    idx = int((v / 255) * (len(RAMP) - 1))
    return RAMP[idx]


def build_svg(img: Image.Image) -> str:
    w, h = img.size
    px = img.load()

    lines = []
    for y in range(h):
        row = "".join(pixel_to_char(px[x, y]) for x in range(w))
        lines.append(row)

    svg_w = w * CELL_W
    svg_h = h * CELL_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'viewBox="0 0 {svg_w:.0f} {svg_h:.0f}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
    )
    parts.append(
        f'<rect width="100%" height="100%" fill="#0d1117"/>'
    )
    parts.append(
        f'<style>'
        f'.row {{ font-size:{FONT_SIZE}px; fill:#c9d1d9; white-space:pre; }}'
        f'.cur {{ fill:#39d353; animation: blink 1s step-start infinite; }}'
        f'@keyframes blink {{ 50% {{ opacity: 0; }} }}'
        f'</style>'
    )

    # Rendered fully visible by default (GitHub shows these via <img>, which
    # does not run SMIL or CSS animation in most browsers, Chrome included).
    # The blinking cursor uses a CSS animation that starts from a visible
    # state, so it degrades to "just visible" instead of "invisible" on
    # browsers that skip the animation.
    for y, row in enumerate(lines):
        ty = (y + 1) * CELL_H - 2
        safe_row = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_row = safe_row.replace(" ", "&#160;")
        parts.append(f'<text class="row" x="0" y="{ty:.1f}">{safe_row}</text>')

    cursor_x = len(lines[-1]) * CELL_W if lines else 0
    cursor_y = (len(lines)) * CELL_H - 2
    parts.append(
        f'<text class="row cur" x="{cursor_x:.1f}" y="{cursor_y:.1f}">_</text>'
    )

    parts.append('</svg>')
    return "".join(parts)


img = Image.open(SRC).convert("L")
svg = build_svg(img)
with open(OUT, "w") as f:
    f.write(svg)
print(f"Wrote {OUT} ({len(svg)} bytes, {img.width}x{img.height} chars)")
