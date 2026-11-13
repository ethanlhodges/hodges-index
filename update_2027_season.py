#!/usr/bin/env python3
"""
Production 2026-27 College Basketball Ranking & Daily Updater Pipeline
----------------------------------------------------------------------
Run this script any day during the 2026-27 season:
    python3 update_2027_season.py
"""

import subprocess
import sys
import urllib.request
from pathlib import Path

from kenpom_engine import DATA_DIR, PRODUCTION_CONFIG, load_season_games


def fetch_latest_2027_data():
    """Download latest 2026-27 schedule/box scores and team results from Bart Torvik."""
    urls = [
        ("https://barttorvik.com/2027_super_sked.json", DATA_DIR / "2027_super_sked.json"),
        ("https://barttorvik.com/2027_team_results.json", DATA_DIR / "2027_team_results.json"),
    ]
    for url, dest in urls:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            dest.write_bytes(resp.read())
    print("✓ Downloaded latest 2026-27 game logs & team records.")


if __name__ == "__main__":
    fetch_latest_2027_data()
    meta_27, games_27 = load_season_games(2027)
    avg_games = (2.0 * len(games_27)) / max(1, len(meta_27))
    auto_prior_w = max(
        0.0,
        PRODUCTION_CONFIG["prior_max_weight"]
        * (1.0 - avg_games / PRODUCTION_CONFIG["prior_fadeout_games"]),
    )
    print(f"✓ Season Status: {len(games_27):,} D-I games completed ({avg_games:.1f} avg games/team).")
    print(f"✓ Dynamic Preseason Prior Weight: w_prior = {auto_prior_w:.2f} (fades to 0.0 at 14.0 games/team).")
    subprocess.run([sys.executable, str(DATA_DIR / "build_digestible_site.py")], check=True)
    subprocess.run([sys.executable, str(DATA_DIR / "render_site.py")], check=True)
    print("✓ Rebuilt live rankings site & daily slate projections!")
