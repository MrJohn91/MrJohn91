#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG, wipes in then rocks slightly."""
import sys

OUT = sys.argv[2] if len(sys.argv) > 2 else "wordmark.svg"

LOGO = [
    "888b     d888 8888888b.       8888888 ",
    "8888b   d8888 888   Y88b        888   ",
    "88888b.d88888 888    888        888   ",
    "888Y88888P888 888   d88P        888   ",
    "888 Y888P 888 8888888P\"         888   ",
    "888  Y8P  888 888   T88b        888   ",
    "888   \"   888 888    T88b       888   ",
    "888       888 888     T88b    8888888 ",
]

FIELDS = [
    ("user", "mrj@synctrack"),
    ("----", "-------------"),
    ("OS", "SyncTrack OS (Germany)"),
    ("Role", "AI Engineer & Software Developer"),
    ("Builds", "Voice agents, automations, AI products"),
    ("Stack", "Python, TypeScript, n8n, Supabase"),
    ("Shell", "/bin/ship-it"),
    ("Status", "open to interesting problems"),
]

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
LOGO_SIZE = 11
LOGO_LH = 15
FIELD_SIZE = 13
FIELD_LH = 22
PAD = 20


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    logo_w = max(len(l) for l in LOGO) * 7.1
    logo_h = len(LOGO) * LOGO_LH
    fields_h = len(FIELDS) * FIELD_LH
    card_h = max(logo_h, fields_h) + PAD * 2
    longest_value = max(len(v) for _, v in FIELDS)
    fields_col_w = 150 + longest_value * 7.6
    card_w = logo_w + fields_col_w + PAD * 3
    cx, cy = logo_w / 2, logo_h / 2

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{card_w:.0f}" height="{card_h:.0f}" '
        f'viewBox="0 0 {card_w:.0f} {card_h:.0f}" font-family="{FONT}">'
    )
    parts.append(
        f'<style>'
        f'.logo{{fill:#39d353;font-size:{LOGO_SIZE}px;white-space:pre;}}'
        f'.k{{fill:#7ee787;font-size:{FIELD_SIZE}px;font-weight:600;}}'
        f'.v{{fill:#c9d1d9;font-size:{FIELD_SIZE}px;}}'
        f'.card{{fill:#0d1117;stroke:#30363d;stroke-width:1;}}'
        f'.rock{{animation:rock 2.6s ease-in-out infinite; animation-delay:2.2s;}}'
        f'@keyframes rock{{0%{{transform:rotate(-4deg) translate({PAD}px,{PAD}px);}}'
        f'50%{{transform:rotate(4deg) translate({PAD}px,{PAD}px);}}'
        f'100%{{transform:rotate(-4deg) translate({PAD}px,{PAD}px);}}}}'
        f'</style>'
    )
    parts.append(
        f'<rect class="card" x="1" y="1" width="{card_w - 2:.0f}" height="{card_h - 2:.0f}" rx="10"/>'
    )

    # left: each logo line fades in top to bottom, then the whole block
    # gently rocks side to side on a loop
    parts.append(f'<g class="rock" style="transform-origin:{cx:.0f}px {cy:.0f}px" transform="translate({PAD},{PAD})">')
    for i, line in enumerate(LOGO):
        y = (i + 1) * LOGO_LH - 3
        begin = i * 0.14
        parts.append(
            f'<text class="logo" x="0" y="{y:.1f}"><tspan opacity="0">{esc(line)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
            f'dur="0.35s" fill="freeze"/></tspan></text>'
        )
    parts.append('</g>')

    # right: neofetch-style field list, fades in once the logo has finished
    fx = logo_w + PAD * 2
    parts.append(f'<g transform="translate({fx:.0f},{PAD})">')
    for i, (k, v) in enumerate(FIELDS):
        y = (i + 1) * FIELD_LH - 6
        begin = 1.3 + i * 0.08
        parts.append(
            f'<text class="k" x="0" y="{y:.1f}"><tspan opacity="0">{esc(k)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.3s" fill="freeze"/></tspan></text>'
        )
        parts.append(
            f'<text class="v" x="150" y="{y:.1f}"><tspan opacity="0">{esc(v)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.3s" fill="freeze"/></tspan></text>'
        )
    parts.append('</g>')

    parts.append('</svg>')
    return "".join(parts)


svg = build_svg()
with open(OUT, "w") as f:
    f.write(svg)
print(f"Wrote {OUT} ({len(svg)} bytes)")
