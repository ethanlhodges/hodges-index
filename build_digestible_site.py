#!/usr/bin/env python3
"""
Generates site_payload.json for the 2026-27 College Basketball Rankings & Daily Slate Hub.
Uses kenpom_engine.py as the single source of truth for all math & hyperparameters.
Dynamically derives:
  - Latest game date (updated_at)
  - Dynamic preseason prior weight w_prior = max(0, 8 * (1 - G_avg / 14))
  - 3-day upcoming & live slate starting from today (or latest completed date)
  - Dynamic KPI summary stats (no hardcoded teams or dates!)
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path

from kenpom_engine import (
    DATA_DIR,
    HIGH_ALTITUDE_TEAMS,
    PRODUCTION_CONFIG,
    load_priors_from_team_results,
    load_season_games,
    solve_model,
)


def build_site_payload():
    # 1. Solve 2025-26 Final Ratings for Preseason Priors
    meta_26, games_26 = load_season_games(2026)
    base_26 = solve_model(
        meta_26,
        games_26,
        zero_ridge_alpha=PRODUCTION_CONFIG["zero_ridge_alpha"],
        recency_decay=PRODUCTION_CONFIG["recency_decay"],
        margin_cap=PRODUCTION_CONFIG["margin_cap"],
        three_pt_luck_weight=PRODUCTION_CONFIG["three_pt_luck_weight"],
        eb_3p_prior_att=PRODUCTION_CONFIG["eb_3p_prior_att"],
        eb_3p_prior_mean=PRODUCTION_CONFIG["eb_3p_prior_mean"],
        altitude_boost=PRODUCTION_CONFIG["altitude_boost"],
    )
    mu_26 = base_26["mu"]
    priors_26 = {
        r["team"]: (r["adj_o"] - mu_26, r["adj_d"] - mu_26)
        for r in base_26["rankings"]
    }

    # 2. Load & Solve Live 2026-27 Season
    meta_27, games_27 = load_season_games(2027)
    avg_g = (2.0 * len(games_27)) / max(1, len(meta_27))
    pw = max(
        0.0,
        PRODUCTION_CONFIG["prior_max_weight"]
        * (1.0 - avg_g / PRODUCTION_CONFIG["prior_fadeout_games"]),
    )

    model_27 = solve_model(
        meta_27,
        games_27,
        priors_map=priors_26,
        prior_weight=pw,
        prior_shrinkage=PRODUCTION_CONFIG["prior_shrinkage"],
        zero_ridge_alpha=PRODUCTION_CONFIG["zero_ridge_alpha"],
        recency_decay=PRODUCTION_CONFIG["recency_decay"],
        margin_cap=PRODUCTION_CONFIG["margin_cap"],
        three_pt_luck_weight=PRODUCTION_CONFIG["three_pt_luck_weight"],
        eb_3p_prior_att=PRODUCTION_CONFIG["eb_3p_prior_att"],
        eb_3p_prior_mean=PRODUCTION_CONFIG["eb_3p_prior_mean"],
        altitude_boost=PRODUCTION_CONFIG["altitude_boost"],
    )

    # Pure 2026-27 Only (No Preseason Prior) solve for toggleable view
    model_27_np = solve_model(
        meta_27,
        games_27,
        priors_map=None,
        prior_weight=0.0,
        zero_ridge_alpha=max(PRODUCTION_CONFIG["zero_ridge_alpha"], 3.5 if avg_g < 8 else 1.5),
        recency_decay=PRODUCTION_CONFIG["recency_decay"],
        margin_cap=PRODUCTION_CONFIG["margin_cap"],
        three_pt_luck_weight=PRODUCTION_CONFIG["three_pt_luck_weight"],
        eb_3p_prior_att=PRODUCTION_CONFIG["eb_3p_prior_att"],
        eb_3p_prior_mean=PRODUCTION_CONFIG["eb_3p_prior_mean"],
        altitude_boost=PRODUCTION_CONFIG["altitude_boost"],
    )

    mu = model_27["mu"]
    mu_np = model_27_np["mu"]
    mu_tempo = model_27["mu_tempo"]
    std_hca = PRODUCTION_CONFIG["std_hca"]
    alt_hca = PRODUCTION_CONFIG["alt_hca"]
    prob_sigma = PRODUCTION_CONFIG["prob_sigma"]

    # Rank Offense & Defense (With Prior)
    teams_raw = model_27["rankings"]
    by_o = sorted(teams_raw, key=lambda x: x["adj_o"], reverse=True)
    o_rk_map = {r["team"]: i for i, r in enumerate(by_o, 1)}
    by_d = sorted(teams_raw, key=lambda x: x["adj_d"])
    d_rk_map = {r["team"]: i for i, r in enumerate(by_d, 1)}

    # Rank Overall, Offense & Defense (No Prior)
    np_raw = model_27_np["rankings"]
    np_by_o = sorted(np_raw, key=lambda x: x["adj_o"], reverse=True)
    np_o_rk = {r["team"]: i for i, r in enumerate(np_by_o, 1)}
    np_by_d = sorted(np_raw, key=lambda x: x["adj_d"])
    np_d_rk = {r["team"]: i for i, r in enumerate(np_by_d, 1)}
    np_map = {r["team"]: r for r in np_raw}

    team_logs = {t: [] for t in meta_27}
    team_lookup = {r["team"]: r for r in teams_raw}

    for g in games_27:
        t1, t2 = g["t1"], g["t2"]
        r1, r2 = team_lookup[t1], team_lookup[t2]
        p1, p2 = int(g["t1_pts"]), int(g["t2_pts"])
        poss = round(g["poss"], 1)
        ortg1 = round(100.0 * p1 / g["poss"], 1)
        ortg2 = round(100.0 * p2 / g["poss"], 1)
        loc1 = "N" if g["neutral"] else "Away"
        loc2 = "N" if g["neutral"] else "Home"
        team_logs[t1].append({
            "date": g["date"][5:], "loc": loc1, "opp": t2, "opp_rk": r2["rank"],
            "win": p1 > p2, "score": f"{p1}-{p2}", "poss": poss, "ortg": ortg1, "drtg": ortg2
        })
        team_logs[t2].append({
            "date": g["date"][5:], "loc": loc2, "opp": t1, "opp_rk": r1["rank"],
            "win": p2 > p1, "score": f"{p2}-{p1}", "poss": poss, "ortg": ortg2, "drtg": ortg1
        })

    teams_list = []
    for r in teams_raw:
        t = r["team"]
        r_np = np_map[t]
        if t in priors_26:
            pr_o, pr_d = priors_26[t]
            prior_em = PRODUCTION_CONFIG["prior_shrinkage"] * (pr_o - pr_d)
        else:
            prior_em = PRODUCTION_CONFIG["new_d1_prior_off"] - PRODUCTION_CONFIG["new_d1_prior_def"]

        teams_list.append({
            "rank": r["rank"],
            "team": t,
            "conf": r["conf"],
            "record": r["record"],
            "gp": r["gp"],
            "adj_em": round(r["adj_em"], 2),
            "adj_o": round(r["adj_o"], 2),
            "adj_d": round(r["adj_d"], 2),
            "o_rk": o_rk_map[t],
            "d_rk": d_rk_map[t],
            "np_rank": r_np["rank"],
            "np_adj_em": round(r_np["adj_em"], 2),
            "np_adj_o": round(r_np["adj_o"], 2),
            "np_adj_d": round(r_np["adj_d"], 2),
            "np_o_rk": np_o_rk[t],
            "np_d_rk": np_d_rk[t],
            "tempo": round(r["tempo"], 1),
            "efg": round(100.0 * r["efg"], 1),
            "tov": round(100.0 * r["tov_rate"], 1),
            "orb": round(100.0 * r["orb_rate"], 1),
            "opp_orb": round(100.0 * r["drb_allow"], 1),
            "vs_prior": round(r["adj_em"] - prior_em, 2),
            "torvik_rk": r["torvik_rank"],
            "alt": 1 if t in HIGH_ALTITUDE_TEAMS else 0,
            "logs": list(reversed(team_logs[t])),  # Most recent game first
        })

    # 3. Dynamic 3-Day Slate starting from US/Eastern today (prevents UTC evening rollover)
    from zoneinfo import ZoneInfo
    eastern_today = datetime.now(ZoneInfo("America/New_York")).date()
    latest_dt = max((g["dt"] for g in games_27), default=datetime.now())
    today_dt = eastern_today
    slate_dates_meta = []
    target_dates = {}
    date_order = {}
    for offset in range(3):
        d = today_dt + timedelta(days=offset)
        # Format without leading zeros to match Torvik's M/D/YY (e.g. 11/12/26)
        key = f"{d.month}/{d.day}/{str(d.year)[-2:]}"
        if offset == 0:
            lbl = f"Today ({d.strftime('%b')} {d.day})"
        else:
            lbl = d.strftime("%a (%b ") + f"{d.day})"
        target_dates[key] = lbl
        date_order[key] = offset
        slate_dates_meta.append({"key": key, "label": lbl})

    with open(DATA_DIR / "2027_super_sked.json") as f:
        raw_sked = json.load(f)

    slate_games = []
    team_info_map = {r["team"]: r for r in teams_list}

    for g in raw_sked:
        d_str = str(g[1])
        if d_str not in target_dates or g[6] == 99:
            continue
        t1, t2 = g[8], g[14]
        if t1 not in team_info_map or t2 not in team_info_map:
            continue

        r1, r2 = team_info_map[t1], team_info_map[t2]
        is_neutral = (int(g[7]) == 1)
        is_final = isinstance(g[50], list) and len(g[50]) >= 35

        est_poss = 0.5 * (r1["tempo"] + r2["tempo"])

        hca_game = 0.0
        if not is_neutral:
            hca_game = std_hca + (alt_hca if r2["alt"] else 0.0)

        ortg1 = r1["adj_o"] + r2["adj_d"] - mu - 0.5 * hca_game
        ortg2 = r2["adj_o"] + r1["adj_d"] - mu + 0.5 * hca_game

        pred_pts1 = round(ortg1 * (est_poss / 100.0), 1)
        pred_pts2 = round(ortg2 * (est_poss / 100.0), 1)
        margin2 = pred_pts2 - pred_pts1

        z = margin2 / prob_sigma
        prob2 = round(100.0 / (1.0 + math.exp(-1.702 * z)), 1)
        prob1 = round(100.0 - prob2, 1)

        fav_team = t2 if margin2 >= 0 else t1
        spread_val = round(abs(margin2), 1)
        thrill_score = round(0.5 * (r1["adj_em"] + r2["adj_em"]) - 0.35 * spread_val, 2)

        slate_games.append({
            "date": d_str,
            "date_idx": date_order[d_str],
            "date_label": target_dates[d_str],
            "t1": t1, "r1": r1["rank"], "rec1": r1["record"],
            "t2": t2, "r2": r2["rank"], "rec2": r2["record"],
            "neutral": is_neutral,
            "pred1": pred_pts1, "pred2": pred_pts2,
            "prob1": prob1, "prob2": prob2,
            "fav": fav_team, "spread": spread_val,
            "torvik_line": str(g[4]),
            "is_final": is_final,
            "actual": str(g[24]) if is_final else "",
            "thrill": thrill_score,
        })

    # Sort chronologically by date first, then by matchup quality within each day
    slate_games.sort(key=lambda x: (x["date_idx"], -x["thrill"]))

    # Dynamic Top KPI Summary
    top1 = teams_list[0]
    off1 = max(teams_list, key=lambda x: x["adj_o"])
    def1 = min(teams_list, key=lambda x: x["adj_d"])
    top80 = [r for r in teams_list if r["rank"] <= 80]
    mover1 = max(top80, key=lambda x: x["vs_prior"])

    return {
        "updated_at": latest_dt.strftime("%b %d, %Y").replace(" 0", " "),
        "games_count": len(games_27),
        "avg_games": round(avg_g, 1),
        "prior_weight": round(pw, 2),
        "mu": round(mu, 2),
        "mu_np": round(mu_np, 2),
        "config": {
            "std_hca": std_hca,
            "alt_hca": alt_hca,
            "prob_sigma": prob_sigma,
            "mu_tempo": round(mu_tempo, 1),
        },
        "kpis": {
            "no1": top1,
            "off1": off1,
            "def1": def1,
            "mover1": mover1,
        },
        "slate_dates": slate_dates_meta,
        "teams": teams_list,
        "slate": slate_games,
    }


if __name__ == "__main__":
    payload = build_site_payload()
    s = json.dumps(payload, separators=(",", ":"))
    (DATA_DIR / "site_payload.json").write_text(s)
    print(f"Built site_payload.json: {len(s):,} bytes | Updated: {payload['updated_at']} | Slate games: {len(payload['slate'])}")
