#!/usr/bin/env python3
"""
Production 2026-27 College Basketball Ranking & Daily Updater Pipeline
----------------------------------------------------------------------
Run this script any day during the 2026-27 season:
    python3 update_2027_season.py

Data sources:
1. Primary: barttorvik.com/2027_super_sked.json & 2027_team_results.json
2. Automated GitHub Actions Fallback: ESPN public NCAA Men's Basketball API
   (site.api.espn.com) backfills completed game box scores & team W-L records
   directly into 2027_super_sked.json & 2027_team_results.json whenever
   CloudFront blocks data-center runner IPs.
"""

import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from kenpom_engine import DATA_DIR, PRODUCTION_CONFIG, load_season_games


def _norm_team(s: str) -> str:
    s = s.lower().replace("é", "e").replace("&", "and").replace("-", " ").replace(".", "")
    s = re.sub(r"\bstate\b", "st", s)
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return " ".join(s.split())


def _parse_made_att(val: str):
    if "-" in str(val):
        a, b = str(val).split("-", 1)
        return float(a or 0), float(b or 0)
    return 0.0, 0.0


def _extract_espn_team_box(stats_list, score_pts: float):
    smap = {s.get("name", ""): s.get("displayValue", "0") for s in stats_list}
    fgm, fga = _parse_made_att(smap.get("fieldGoalsMade-fieldGoalsAttempted", "0-0"))
    tpm, tpa = _parse_made_att(smap.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted", "0-0"))
    ftm, fta = _parse_made_att(smap.get("freeThrowsMade-freeThrowsAttempted", "0-0"))
    orb = float(smap.get("offensiveRebounds", 0) or 0)
    drb = float(smap.get("defensiveRebounds", 0) or 0)
    reb = float(smap.get("totalRebounds", orb + drb) or (orb + drb))
    ast = float(smap.get("assists", 0) or 0)
    stl = float(smap.get("steals", 0) or 0)
    blk = float(smap.get("blocks", 0) or 0)
    tov = float(smap.get("totalTurnovers", smap.get("turnovers", 0)) or 0)
    pf = float(smap.get("fouls", 0) or 0)
    return [fgm, fga, tpm, tpa, ftm, fta, orb, drb, reb, ast, stl, blk, tov, pf, float(score_pts)]


def backfill_from_espn():
    """Backfill any newly completed games up through today using ESPN's public scoreboard & boxscore API."""
    sked_path = DATA_DIR / "2027_super_sked.json"
    teams_path = DATA_DIR / "2027_team_results.json"
    sked = json.loads(sked_path.read_text())
    teams = json.loads(teams_path.read_text())

    today_et = datetime.now(ZoneInfo("America/New_York")).date()

    # Find dates <= today_et that have uncompleted games in 2027_super_sked.json
    pending_by_date = {}
    for idx, g in enumerate(sked):
        if g[6] == 99:
            continue
        if isinstance(g[50], list) and len(g[50]) >= 35:
            continue
        try:
            dt = datetime.strptime(str(g[1]), "%m/%d/%y").date()
        except ValueError:
            continue
        if dt <= today_et:
            pending_by_date.setdefault(dt, []).append(idx)

    updated_games = 0
    for dt, game_indices in sorted(pending_by_date.items()):
        ymd = dt.strftime("%Y%m%d")
        sb_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={ymd}&groups=50&limit=300"
        try:
            req = urllib.request.Request(sb_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            sb_data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        except Exception as e:
            print(f"  ! ESPN scoreboard fetch failed for {ymd}: {e}")
            continue

        espn_events = []
        for ev in sb_data.get("events", []):
            if not ev.get("status", {}).get("type", {}).get("completed", False):
                continue
            comp = ev["competitions"][0]
            c0, c1 = comp["competitors"][0], comp["competitors"][1]
            n0 = {_norm_team(c0["team"].get(k, "")) for k in ("location", "shortDisplayName", "abbreviation", "displayName")}
            n1 = {_norm_team(c1["team"].get(k, "")) for k in ("location", "shortDisplayName", "abbreviation", "displayName")}
            espn_events.append((ev["id"], n0, n1, c0, c1))

        if not espn_events:
            continue

        for idx in game_indices:
            g = sked[idx]
            t1_raw, t2_raw = str(g[8]), str(g[14])
            t1_n, t2_n = _norm_team(t1_raw), _norm_team(t2_raw)

            # Match both teams first, then single-team match on same date
            matches = [e for e in espn_events if (t1_n in e[1] and t2_n in e[2]) or (t1_n in e[2] and t2_n in e[1])]
            if not matches:
                matches = [e for e in espn_events if t1_n in e[1] or t1_n in e[2] or t2_n in e[1] or t2_n in e[2]]
            if not matches:
                continue

            ev_id, n0, n1, c0, c1 = matches[0]
            # Determine which competitor is t1 vs t2
            if t1_n in n0 or t2_n in n1:
                comp1, comp2 = c0, c1
            elif t1_n in n1 or t2_n in n0:
                comp1, comp2 = c1, c0
            else:
                comp1, comp2 = (c0, c1) if c0.get("homeAway") == "away" else (c1, c0)

            id1 = str(comp1["team"]["id"])
            id2 = str(comp2["team"]["id"])
            pts1 = float(comp1.get("score", 0) or 0)
            pts2 = float(comp2.get("score", 0) or 0)
            if pts1 <= 0 and pts2 <= 0:
                continue

            # Fetch full boxscore from ESPN summary endpoint
            sum_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event={ev_id}"
            try:
                sreq = urllib.request.Request(sum_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                sum_data = json.loads(urllib.request.urlopen(sreq, timeout=15).read())
            except Exception:
                continue

            bteams = sum_data.get("boxscore", {}).get("teams", [])
            if len(bteams) < 2:
                continue

            bmap = {str(bt.get("team", {}).get("id", "")): bt.get("statistics", []) for bt in bteams}
            if id1 not in bmap or id2 not in bmap:
                continue

            stats1 = _extract_espn_team_box(bmap[id1], pts1)
            stats2 = _extract_espn_team_box(bmap[id2], pts2)
            if stats1[1] <= 0 or stats2[1] <= 0:
                continue

            # Standard Dean Oliver / Torvik possessions formula: FGA - ORB + TOV + 0.475 * FTA
            poss1 = stats1[1] - stats1[6] + stats1[12] + 0.475 * stats1[5]
            poss2 = stats2[1] - stats2[6] + stats2[12] + 0.475 * stats2[5]
            poss = round(0.5 * (poss1 + poss2), 4)

            winner = t1_raw if pts1 > pts2 else t2_raw
            loser = t2_raw if pts1 > pts2 else t1_raw
            hi_pts, lo_pts = int(max(pts1, pts2)), int(min(pts1, pts2))

            box_arr = (
                [str(g[1]), 200.0, t1_raw, t2_raw]
                + stats1
                + stats2
                + [poss, "", winner, loser]
            )
            g[24] = f"{winner}, {hi_pts}-{lo_pts}"
            g[25] = poss
            g[50] = box_arr
            updated_games += 1

    if updated_games > 0:
        # Recompute team W-L records in 2027_team_results.json
        wl = {r[1]: [0, 0] for r in teams}
        for g in sked:
            if isinstance(g[50], list) and len(g[50]) >= 35:
                t1, t2 = g[8], g[14]
                p1, p2 = float(g[50][18]), float(g[50][33])
                if t1 in wl:
                    wl[t1][0 if p1 > p2 else 1] += 1
                if t2 in wl:
                    wl[t2][0 if p2 > p1 else 1] += 1
        for r in teams:
            if r[1] in wl:
                r[3] = f"{wl[r[1]][0]}-{wl[r[1]][1]}"

        sked_path.write_text(json.dumps(sked))
        teams_path.write_text(json.dumps(teams))
        print(f"✓ Backfilled {updated_games} completed games & updated W-L records via ESPN API.")
    else:
        print("✓ ESPN API check complete (all completed games through today are already recorded).")


def fetch_latest_2027_data():
    """Download latest 2026-27 schedule/box scores from Bart Torvik, with automatic ESPN API fallback."""
    urls = [
        ("https://barttorvik.com/2027_super_sked.json", DATA_DIR / "2027_super_sked.json"),
        ("https://barttorvik.com/2027_team_results.json", DATA_DIR / "2027_team_results.json"),
    ]
    headers = {
        "User-Agent": "HodgesIndex/1.0 (+https://ethanlhodges.github.io/hodges-index/)",
        "Accept": "application/json",
    }
    try:
        for url, dest in urls:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                if len(data) > 1000:
                    dest.write_bytes(data)
        print("✓ Downloaded latest 2026-27 game logs & team records from Bart Torvik.")
    except Exception as exc:
        print(f"! Notice: Bart Torvik returned ({exc}); running ESPN boxscore backfill...")
        backfill_from_espn()


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
