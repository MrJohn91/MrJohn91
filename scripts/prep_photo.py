#!/usr/bin/env python3
"""Resize and normalize a source photo for ASCII conversion."""
import sys
from PIL import Image, ImageOps, ImageEnhance

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"

# ASCII cells are roughly twice as tall as wide, so undersample rows.
COLS = 90

img = Image.open(SRC).convert("L")
img = ImageOps.autocontrast(img, cutoff=1)
img = ImageEnhance.Contrast(img).enhance(1.15)

aspect = img.height / img.width
rows = int(COLS * aspect * 0.5)
img = img.resize((COLS, rows), Image.LANCZOS)

img.save(OUT)
print(f"Prepped {SRC} -> {OUT} ({COLS}x{rows})")
