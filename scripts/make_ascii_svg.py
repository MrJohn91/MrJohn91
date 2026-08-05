#!/usr/bin/env python3
"""Convert a prepped grayscale image into a self-typing monochrome ASCII SVG."""
import sys
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "mrj-ascii.svg"

# Dense-to-sparse ramp, darkest first.
RAMP = "@%#*+=-:. "

CELL_W = 6.2
CELL_H = 11.5
FONT_SIZE = 12
TYPE_DURATION_PER_CHAR = 0.006  # seconds


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
        f'.cur {{ fill:#39d353; }}'
        f'</style>'
    )

    delay = 0.0
    for y, row in enumerate(lines):
        ty = (y + 1) * CELL_H - 2
        parts.append(f'<text class="row" x="0" y="{ty:.1f}">')
        for x, ch in enumerate(row):
            safe = ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if safe == " ":
                safe = "&#160;"
            begin = f"{delay:.3f}s"
            parts.append(
                f'<tspan opacity="0" x="{x * CELL_W:.1f}">{safe}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin}" '
                f'dur="0.01s" fill="freeze"/></tspan>'
            )
            delay += TYPE_DURATION_PER_CHAR
        parts.append('</text>')

    # blinking cursor at the end of the typing animation
    cursor_x = len(lines[-1]) * CELL_W if lines else 0
    cursor_y = (len(lines)) * CELL_H - 2
    parts.append(
        f'<text class="row cur" x="{cursor_x:.1f}" y="{cursor_y:.1f}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.01s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="{delay:.3f}s" repeatCount="indefinite"/>'
        f'_</text>'
    )

    parts.append('</svg>')
    return "".join(parts)


img = Image.open(SRC).convert("L")
svg = build_svg(img)
with open(OUT, "w") as f:
    f.write(svg)
print(f"Wrote {OUT} ({len(svg)} bytes, {img.width}x{img.height} chars)")
