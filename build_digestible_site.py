#!/usr/bin/env python3
"""
Generates site_payload.json and daily historical snapshots (history/YYYY-MM-DD.json)
for the 2026-27 College Basketball Rankings, Daily Slate & Performance Tracker.
Uses kenpom_engine.py as the single source of truth for all math & hyperparameters.
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from kenpom_engine import (
    DATA_DIR,
    HIGH_ALTITUDE_TEAMS,
    PRODUCTION_CONFIG,
    load_priors_from_team_results,
    load_season_games,
    solve_model,
)

HISTORY_DIR = DATA_DIR / "history"


def build_walk_forward_history(meta_27, games_27, priors_26, mu_26, vegas_map):
    """
    Computes strictly out-of-sample (pre-game) rankings and game predictions for every
    completed game date of the 2026-27 season, evaluates Straight-Up and Against the Spread (ATS)
    performance vs Vegas closing lines, writes full daily snapshots to history/YYYY-MM-DD.json,
    and returns a compact summary for site_payload.json.
    """
    HISTORY_DIR.mkdir(exist_ok=True)
    std_hca = PRODUCTION_CONFIG["std_hca"]
    alt_hca = PRODUCTION_CONFIG["alt_hca"]
    prob_sigma = PRODUCTION_CONFIG["prob_sigma"]

    all_dates = sorted({g["date"] for g in games_27})
    days_payload = []

    total_games = 0
    total_hits = 0
    total_ats_w = 0
    total_ats_l = 0
    total_ats_p = 0
    total_val_w = 0
    total_val_l = 0
    total_val_p = 0
    all_errs = []

    # Calibration buckets: 50-60%, 60-70%, 70-80%, 80-90%, 90-100%
    bucket_defs = [
        ("50–60%", 50.0, 60.0),
        ("60–70%", 60.0, 70.0),
        ("70–80%", 70.0, 80.0),
        ("80–90%", 80.0, 90.0),
        ("90%+", 90.0, 100.1),
    ]
    bucket_stats = {lbl: {"n": 0, "hits": 0, "prob_sum": 0.0} for lbl, _, _ in bucket_defs}

    for d_str in all_dates:
        prior_games = [g for g in games_27 if g["date"] < d_str]
        day_games = [g for g in games_27 if g["date"] == d_str]
        if len(day_games) < 2:
            continue

        dt_obj = datetime.strptime(d_str, "%Y-%m-%d")
        if not prior_games:
            # Opening day: pure preseason priors
            mu = mu_26
            mu_tempo = 68.5
            pw = PRODUCTION_CONFIG["prior_max_weight"]
            raw_list = []
            for t, m in meta_27.items():
                po, pd = priors_26.get(
                    t,
                    (PRODUCTION_CONFIG["new_d1_prior_off"], PRODUCTION_CONFIG["new_d1_prior_def"]),
                )
                s = PRODUCTION_CONFIG["prior_shrinkage"] if t in priors_26 else 1.0
                ao = mu + s * po
                ad = mu + s * pd
                raw_list.append({
                    "team": t,
                    "conf": m["conf"],
                    "record": "0-0",
                    "gp": 0,
                    "adj_o": round(ao, 2),
                    "adj_d": round(ad, 2),
                    "adj_em": round(ao - ad, 2),
                    "tempo": 68.5,
                })
            raw_list.sort(key=lambda x: x["adj_em"], reverse=True)
            for idx, r in enumerate(raw_list, 1):
                r["rank"] = idx
            tmap = {
                r["team"]: {**r, "alt": 1 if r["team"] in HIGH_ALTITUDE_TEAMS else 0}
                for r in raw_list
            }
            rankings_snapshot = raw_list
        else:
            avg_g = (2.0 * len(prior_games)) / max(1, len(meta_27))
            pw = max(
                0.0,
                PRODUCTION_CONFIG["prior_max_weight"]
                * (1.0 - avg_g / PRODUCTION_CONFIG["prior_fadeout_games"]),
            )
            res = solve_model(
                meta_27,
                prior_games,
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
                ref_date=dt_obj,
            )
            mu = res["mu"]
            mu_tempo = res["mu_tempo"]
            wl_prior = {t: [0, 0] for t in meta_27}
            for pg in prior_games:
                w_t = pg["t1"] if pg["t1_pts"] > pg["t2_pts"] else pg["t2"]
                l_t = pg["t2"] if pg["t1_pts"] > pg["t2_pts"] else pg["t1"]
                wl_prior[w_t][0] += 1
                wl_prior[l_t][1] += 1

            rankings_snapshot = []
            for r in res["rankings"]:
                t = r["team"]
                rankings_snapshot.append({
                    "rank": r["rank"],
                    "team": t,
                    "conf": r["conf"],
                    "record": f"{wl_prior[t][0]}-{wl_prior[t][1]}",
                    "gp": r["gp"],
                    "adj_o": round(r["adj_o"], 2),
                    "adj_d": round(r["adj_d"], 2),
                    "adj_em": round(r["adj_em"], 2),
                    "tempo": round(r["tempo"], 1),
                })
            tmap = {
                r["team"]: {**r, "alt": 1 if r["team"] in HIGH_ALTITUDE_TEAMS else 0}
                for r in rankings_snapshot
            }

        day_picks = []
        day_hits = 0
        day_ats_w = 0
        day_ats_l = 0
        day_ats_p = 0
        day_val_w = 0
        day_val_l = 0
        day_val_p = 0
        day_errs = []

        for g in day_games:
            t1, t2 = g["t1"], g["t2"]
            r1, r2 = tmap[t1], tmap[t2]
            est_poss = r1["tempo"] + r2["tempo"] - mu_tempo
            hca = 0.0 if g["neutral"] else (std_hca + (alt_hca if r2["alt"] else 0.0))

            o1 = r1["adj_o"] + r2["adj_d"] - mu - 0.5 * hca
            o2 = r2["adj_o"] + r1["adj_d"] - mu + 0.5 * hca
            pred1 = round(o1 * (est_poss / 100.0), 1)
            pred2 = round(o2 * (est_poss / 100.0), 1)
            pred_margin2 = pred2 - pred1

            z = pred_margin2 / prob_sigma
            prob2 = round(100.0 / (1.0 + math.exp(-1.702 * z)), 1)
            prob1 = round(100.0 - prob2, 1)

            fav = t2 if pred_margin2 >= 0 else t1
            spread = round(abs(pred_margin2), 1)
            fav_prob = max(prob1, prob2)

            p1, p2 = int(g["t1_pts"]), int(g["t2_pts"])
            actual_winner = t2 if p2 > p1 else t1
            actual_margin2 = float(p2 - p1)
            hit = (fav == actual_winner)
            err = round(abs(pred_margin2 - actual_margin2), 1)

            if hit:
                day_hits += 1
                total_hits += 1
            total_games += 1
            day_errs.append(err)
            all_errs.append(err)

            # Evaluate ATS vs Vegas closing line if available
            v_key = f"{d_str}|{t1}|{t2}"
            vegas_str = ""
            ats_pick = ""
            ats_res = ""
            is_value = False
            val_edge = 0.0
            val_type = ""
            if v_key in vegas_map:
                v_info = vegas_map[v_key]
                v_fav = v_info["fav"]
                v_spr = float(v_info["spread"])
                v_dog = t1 if v_fav == t2 else t2
                vegas_str = f"{v_fav} -{v_spr:.1f}" if v_spr > 0 else "PK"
                # Expected Team 2 margin implied by Vegas line
                v_m2 = v_spr if v_fav == t2 else -v_spr
                val_edge = round(abs(pred_margin2 - v_m2), 1)
                if abs(pred_margin2 - v_m2) >= 0.05:
                    # Does model like Team 2 more than Vegas does?
                    pick_t2 = pred_margin2 > v_m2
                    if pick_t2:
                        ats_pick = f"{t2} {'-' + str(v_spr) if v_fav == t2 else '+' + str(v_spr)}"
                    else:
                        ats_pick = f"{t1} {'-' + str(v_spr) if v_fav == t1 else '+' + str(v_spr)}"

                    # Identify high-value mispriced spreads (Underdog Flips or Competitive Dog Edges)
                    backing_dog = (pick_t2 and v_fav == t1) or ((not pick_t2) and v_fav == t2)
                    is_flip = (fav != v_fav and 1.5 <= val_edge <= 7.5)
                    is_dog_val = (backing_dog and 2.5 <= val_edge <= 7.0 and v_spr <= 12.0)
                    is_value = bool(is_flip or is_dog_val)
                    val_type = "Flip" if is_flip else ("Dog Edge" if is_dog_val else "")

                    if actual_margin2 == v_m2:
                        ats_res = "P"
                        day_ats_p += 1
                        total_ats_p += 1
                        if is_value:
                            day_val_p += 1
                            total_val_p += 1
                    elif (pick_t2 and actual_margin2 > v_m2) or ((not pick_t2) and actual_margin2 < v_m2):
                        ats_res = "W"
                        day_ats_w += 1
                        total_ats_w += 1
                        if is_value:
                            day_val_w += 1
                            total_val_w += 1
                    else:
                        ats_res = "L"
                        day_ats_l += 1
                        total_ats_l += 1
                        if is_value:
                            day_val_l += 1
                            total_val_l += 1

            for b_lbl, b_lo, b_hi in bucket_defs:
                if b_lo <= fav_prob < b_hi:
                    bucket_stats[b_lbl]["n"] += 1
                    bucket_stats[b_lbl]["hits"] += (1 if hit else 0)
                    bucket_stats[b_lbl]["prob_sum"] += fav_prob
                    break

            thrill = round(0.5 * (r1["adj_em"] + r2["adj_em"]) - 0.35 * spread, 2)
            day_picks.append({
                "t1": t1, "r1": r1["rank"],
                "t2": t2, "r2": r2["rank"],
                "neutral": g["neutral"],
                "fav": fav, "spread": spread, "prob": fav_prob,
                "pred1": pred1, "pred2": pred2,
                "p1": p1, "p2": p2,
                "winner": actual_winner,
                "hit": hit,
                "err": err,
                "vegas": vegas_str,
                "ats_pick": ats_pick,
                "ats_res": ats_res,
                "is_value": is_value,
                "val_edge": val_edge,
                "val_type": val_type,
                "thrill": thrill,
            })

        day_picks.sort(key=lambda x: -x["thrill"])
        day_mae = round(sum(day_errs) / max(1, len(day_errs)), 2)
        day_win_pct = round(100.0 * day_hits / max(1, len(day_picks)), 1)
        day_ats_pct = round(100.0 * day_ats_w / max(1, day_ats_w + day_ats_l), 1)
        day_val_pct = round(100.0 * day_val_w / max(1, day_val_w + day_val_l), 1)
        label = dt_obj.strftime("%a, %b ") + str(dt_obj.day)

        full_snapshot = {
            "date": d_str,
            "label": label,
            "games_count": len(day_picks),
            "correct": day_hits,
            "win_pct": day_win_pct,
            "ats_w": day_ats_w,
            "ats_l": day_ats_l,
            "ats_p": day_ats_p,
            "ats_pct": day_ats_pct,
            "val_w": day_val_w,
            "val_l": day_val_l,
            "val_p": day_val_p,
            "val_pct": day_val_pct,
            "mae": day_mae,
            "prior_weight": round(pw, 2),
            "picks": day_picks,
            "rankings": rankings_snapshot,
        }
        (HISTORY_DIR / f"{d_str}.json").write_text(json.dumps(full_snapshot, separators=(",", ":")))

        days_payload.append({
            "date": d_str,
            "label": label,
            "games_count": len(day_picks),
            "correct": day_hits,
            "win_pct": day_win_pct,
            "ats_w": day_ats_w,
            "ats_l": day_ats_l,
            "ats_p": day_ats_p,
            "ats_pct": day_ats_pct,
            "val_w": day_val_w,
            "val_l": day_val_l,
            "val_p": day_val_p,
            "val_pct": day_val_pct,
            "mae": day_mae,
            "prior_weight": round(pw, 2),
            "picks": day_picks,
            "top40": rankings_snapshot[:40],
        })

    days_payload.reverse()

    buckets_out = []
    for b_lbl, _, _ in bucket_defs:
        st = bucket_stats[b_lbl]
        n = st["n"]
        buckets_out.append({
            "bucket": b_lbl,
            "games": n,
            "correct": st["hits"],
            "expected_pct": round(st["prob_sum"] / n, 1) if n > 0 else 0.0,
            "actual_pct": round(100.0 * st["hits"] / n, 1) if n > 0 else 0.0,
        })

    history_summary = {
        "total_games": total_games,
        "correct": total_hits,
        "win_pct": round(100.0 * total_hits / max(1, total_games), 1),
        "ats_w": total_ats_w,
        "ats_l": total_ats_l,
        "ats_p": total_ats_p,
        "ats_pct": round(100.0 * total_ats_w / max(1, total_ats_w + total_ats_l), 1),
        "val_w": total_val_w,
        "val_l": total_val_l,
        "val_p": total_val_p,
        "val_pct": round(100.0 * total_val_w / max(1, total_val_w + total_val_l), 1),
        "mae": round(sum(all_errs) / max(1, len(all_errs)), 2),
        "buckets": buckets_out,
        "days": days_payload,
    }
    (HISTORY_DIR / "performance_history.json").write_text(
        json.dumps(history_summary, separators=(",", ":"))
    )
    return history_summary


def build_site_payload():
    # 1. Load Un-Shrunk 2025-26 Final Efficiency Ratings for Preseason Priors
    mu_26 = 106.5
    priors_26 = load_priors_from_team_results(2026)

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

    # 3. Dynamic 3-Day Slate starting from US/Eastern today
    eastern_today = datetime.now(ZoneInfo("America/New_York")).date()
    today_dt = eastern_today
    slate_dates_meta = []
    target_dates = {}
    date_order = {}
    for offset in range(3):
        d = today_dt + timedelta(days=offset)
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

    vegas_path = DATA_DIR / "vegas_lines_2027.json"
    vegas_map = json.loads(vegas_path.read_text()) if vegas_path.exists() else {}

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

        est_poss = r1["tempo"] + r2["tempo"] - mu_tempo

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

        d_iso = datetime.strptime(d_str, "%m/%d/%y").strftime("%Y-%m-%d")
        v_info = vegas_map.get(f"{d_iso}|{t1}|{t2}")
        vegas_str = ""
        is_value = False
        val_pick = ""
        val_edge = 0.0
        val_type = ""
        if v_info:
            v_fav = v_info["fav"]
            v_spr = float(v_info["spread"])
            v_dog = t1 if v_fav == t2 else t2
            vegas_str = f"{v_fav} -{v_spr:.1f}" if v_spr > 0 else "PK"
            v_m2 = v_spr if v_fav == t2 else -v_spr
            val_edge = round(abs(margin2 - v_m2), 1)
            pick_t2 = margin2 > v_m2
            backing_dog = (pick_t2 and v_fav == t1) or ((not pick_t2) and v_fav == t2)
            is_flip = (fav_team != v_fav and 1.5 <= val_edge <= 7.5)
            is_dog_val = (backing_dog and 2.5 <= val_edge <= 7.0 and v_spr <= 12.0)
            is_value = bool(is_flip or is_dog_val)
            if is_value:
                val_pick = f"{v_dog} +{v_spr:.1f}"
                val_type = "Flip" if is_flip else "Dog Edge"

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
            "vegas": vegas_str,
            "is_value": is_value,
            "val_pick": val_pick,
            "val_edge": val_edge,
            "val_type": val_type,
            "torvik_line": str(g[4]),
            "is_final": is_final,
            "actual": str(g[24]) if is_final else "",
            "thrill": thrill_score,
        })

    # Sort chronologically by date first, then by matchup quality within each day
    slate_games.sort(key=lambda x: (x["date_idx"], -x["thrill"]))

    # 4. Build Walk-Forward Historical Rankings & Daily Picks Performance
    history_data = build_walk_forward_history(meta_27, games_27, priors_26, mu_26, vegas_map)

    # Also archive today's pre-game rankings & today's slate predictions to history/YYYY-MM-DD_pregame.json
    today_iso = eastern_today.strftime("%Y-%m-%d")
    today_key = f"{eastern_today.month}/{eastern_today.day}/{str(eastern_today.year)[-2:]}"
    today_pregame = {
        "date": today_iso,
        "prior_weight": round(pw, 2),
        "slate_picks": [sg for sg in slate_games if sg["date"] == today_key],
        "rankings": [
            {
                "rank": r["rank"], "team": r["team"], "conf": r["conf"],
                "record": r["record"], "gp": r["gp"],
                "adj_em": r["adj_em"], "adj_o": r["adj_o"], "adj_d": r["adj_d"],
                "tempo": r["tempo"],
            }
            for r in teams_list
        ],
    }
    (HISTORY_DIR / f"{today_iso}_pregame.json").write_text(
        json.dumps(today_pregame, separators=(",", ":"))
    )

    top1 = teams_list[0]
    off1 = max(teams_list, key=lambda x: x["adj_o"])
    def1 = min(teams_list, key=lambda x: x["adj_d"])
    top80 = [r for r in teams_list if r["rank"] <= 80]
    mover1 = max(top80, key=lambda x: x["vs_prior"])

    return {
        "updated_at": eastern_today.strftime("%b %d, %Y").replace(" 0", " "),
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
        "history": history_data,
    }


if __name__ == "__main__":
    payload = build_site_payload()
    s = json.dumps(payload, separators=(",", ":"))
    (DATA_DIR / "site_payload.json").write_text(s)
    h = payload["history"]
    print(
        f"Built site_payload.json: {len(s):,} bytes | Updated: {payload['updated_at']} | "
        f"Slate games: {len(payload['slate'])} | History: {h['correct']}/{h['total_games']} ({h['win_pct']}%, MAE {h['mae']})"
    )
