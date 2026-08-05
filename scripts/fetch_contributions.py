#!/usr/bin/env python3
"""Scrape real daily contribution counts from GitHub's public,
unauthenticated contributions endpoint. No token needed."""
import json
import os
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "MrJohn91"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("table.ContributionCalendar-grid td.ContributionCalendar-day")
    if not cells:
        # newer GitHub markup uses <td> with data-date directly, no wrapping table class
        cells = soup.select("td[data-date]")
    for td in cells:
        date = td.get("data-date")
        level = td.get("data-level")
        if date is None:
            continue
        tooltip_id = td.get("id")
        count = 0
        if tooltip_id:
            tip = soup.select_one(f'tool-tip[for="{tooltip_id}"]')
            if tip:
                text = tip.text.strip()
                digits = "".join(ch for ch in text.split(" ")[0] if ch.isdigit())
                count = int(digits) if digits else 0
        days.append({"date": date, "count": count, "level": int(level) if level else 0})
    return days


def compute_stats(days):
    days_sorted = sorted(days, key=lambda d: d["date"])
    total = sum(d["count"] for d in days_sorted)

    current_streak = 0
    for d in reversed(days_sorted):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days_sorted:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best = max(days_sorted, key=lambda d: d["count"], default=None)

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best,
    }


days = fetch_days()
if not days:
    print("WARNING: no contribution cells found, GitHub markup may have changed", file=sys.stderr)
stats = compute_stats(days) if days else {}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump({"username": USERNAME, "days": days, "stats": stats}, f)

print(f"Fetched {len(days)} days for {USERNAME}. Stats: {stats}")
