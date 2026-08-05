#!/usr/bin/env python3
"""Render fetched contribution data into an animated SVG heatmap.
Cells reveal one by one, left to right, like the real calendar filling in."""
import datetime
import json
import sys

DATA = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"

CELL = 11
GAP = 3
STEP = CELL + GAP
PAD_LEFT = 28
PAD_TOP = 20
PAD_BOTTOM = 30

LEVEL_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_weeks(days):
    by_date = {d["date"]: d for d in days}
    if not days:
        return []
    dates = sorted(by_date.keys())
    start = datetime.date.fromisoformat(dates[0])
    end = datetime.date.fromisoformat(dates[-1])

    # align start to the preceding Sunday so columns are full weeks
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    cur = start
    week = []
    while cur <= end:
        iso = cur.isoformat()
        entry = by_date.get(iso, {"date": iso, "count": 0, "level": 0})
        week.append(entry)
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur += datetime.timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append({"date": None, "count": 0, "level": 0})
        weeks.append(week)
    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        first_valid = next((d for d in week if d["date"]), None)
        if not first_valid:
            continue
        m = datetime.date.fromisoformat(first_valid["date"]).month
        if m != last_month:
            labels.append((wi, MONTH_NAMES[m - 1]))
            last_month = m
    return labels


def build_svg(payload):
    days = payload.get("days", [])
    stats = payload.get("stats", {})
    weeks = load_weeks(days)
    n_weeks = len(weeks)

    grid_w = n_weeks * STEP
    grid_h = 7 * STEP
    svg_w = PAD_LEFT + grid_w + 10
    svg_h = PAD_TOP + grid_h + PAD_BOTTOM

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="#0d1117"/>')
    parts.append('<style>.lbl{fill:#8b949e;font-size:10px;}</style>')

    for wi, label in month_labels(weeks):
        x = PAD_LEFT + wi * STEP
        parts.append(f'<text class="lbl" x="{x}" y="{PAD_TOP - 6}">{label}</text>')

    dow_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for di, label in dow_labels.items():
        y = PAD_TOP + di * STEP + CELL - 1
        parts.append(f'<text class="lbl" x="0" y="{y}">{label}</text>')

    delay = 0.0
    delay_step = 0.9 / max(n_weeks * 7, 1)
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if not day["date"]:
                continue
            x = PAD_LEFT + wi * STEP
            y = PAD_TOP + di * STEP
            level = min(day.get("level", 0), 4)
            color = LEVEL_COLORS[level]
            title = f'{day["date"]}: {day["count"]} contribution(s)'
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{color}" opacity="0"><title>{title}</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" '
                f'dur="0.25s" fill="freeze"/></rect>'
            )
            delay += delay_step

    total = stats.get("total", 0)
    longest = stats.get("longest_streak", 0)
    current = stats.get("current_streak", 0)
    summary = f'{total} contributions in the last year   longest streak {longest} days   current streak {current} days'
    parts.append(
        f'<text class="lbl" x="{PAD_LEFT}" y="{svg_h - 10}" opacity="0">{summary}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.4s" fill="freeze"/>'
        f'</text>'
    )

    parts.append('</svg>')
    return "".join(parts)


with open(DATA) as f:
    payload = json.load(f)

svg = build_svg(payload)
with open(OUT, "w") as f:
    f.write(svg)
print(f"Wrote {OUT} ({len(svg)} bytes)")
