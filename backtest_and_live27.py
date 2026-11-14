#!/usr/bin/env python3
"""
Walk-Forward Out-of-Sample Backtester & Live 2026-27 Bayesian Prior Updater
---------------------------------------------------------------------------
1. Walk-Forward Backtester (2025-26 Season):
   Trains strictly on games played BEFORE Date T, and predicts every D-I game
   played inside window [T, T + step) across the entire season (Dec 1 -> April).
   Evaluates:
     - Spread MAE (Mean Absolute Error in points)
     - Spread RMSE (Root Mean Squared Error in points)
     - Straight-Up Winner Accuracy (%)
     - Calibration Log-Loss (cross-entropy of predicted win probabilities)

2. Live 2026-27 Season Rankings with Prior Blending:
   Since 2026-27 is in Week 1 (385 games completed, 258 D-I vs D-I through Nov 7, 2026),
   pure OLS/Ridge without priors has disconnected sub-graphs. We demonstrate how KenPom
   and Torvik solve early-season rankings: using last season's final ratings (shrunk toward
   the D-I average) as the Bayesian Ridge Prior target (x_0), so:
       Objective = || W^(1/2) (X x - y) ||^2 + lambda * || x - x_prior ||^2
"""

import json
import math
from datetime import datetime
from pathlib import Path
import numpy as np

from kenpom_engine import load_d1_games, solve_kenpom_ridge, HIGH_ALTITUDE_TEAMS

DATA_DIR = Path(__file__).parent


def load_season_games(year_prefix: int):
    """Load D-I games for a specific Torvik season file (2026 = 2025-26, 2027 = 2026-27)."""
    sked_file = DATA_DIR / f"{year_prefix}_super_sked.json"
    teams_file = DATA_DIR / f"{year_prefix}_team_results.json"

    with open(teams_file, "r") as f:
        raw_teams = json.load(f)

    team_meta = {}
    for row in raw_teams:
        name = row[1]
        team_meta[name] = {
            "name": name,
            "conf": row[2],
            "record": row[3],
            "torvik_rank": int(row[0]),
            "torvik_adjo": float(row[4]),
            "torvik_adjd": float(row[6]),
        }

    with open(sked_file, "r") as f:
        raw_games = json.load(f)

    games = []
    dates = []
    for g in raw_games:
        if g[6] == 99 or not isinstance(g[50], list) or len(g[50]) < 35:
            continue
        t1, t2 = g[8], g[14]
        if t1 not in team_meta or t2 not in team_meta:
            continue
        poss = float(g[25]) if g[25] else 0.0
        if poss <= 30:
            continue
        try:
            dt = datetime.strptime(g[1], "%m/%d/%y")
        except ValueError:
            continue
        dates.append(dt)

        box = g[50]
        games.append({
            "date": dt.strftime("%Y-%m-%d"),
            "dt": dt,
            "game_type": int(g[6]),
            "t1": t1,
            "t2": t2,
            "neutral": (int(g[7]) == 1),
            "poss": round(poss, 2),
            "t1_pts": float(box[18]),
            "t2_pts": float(box[33]),
            "t1_3pm": float(box[6]),
            "t1_3pa": float(box[7]),
            "t2_3pm": float(box[21]),
            "t2_3pa": float(box[22]),
            "t1_fga": float(box[5]),
            "t1_fgm": float(box[4]),
            "t1_fta": float(box[9]),
            "t1_orb": float(box[10]),
            "t1_drb": float(box[11]),
            "t1_tov": float(box[14]),
            "t2_fga": float(box[20]),
            "t2_fgm": float(box[19]),
            "t2_fta": float(box[24]),
            "t2_orb": float(box[25]),
            "t2_drb": float(box[26]),
            "t2_tov": float(box[29]),
        })

    games.sort(key=lambda x: x["dt"])
    max_date = max(dates) if dates else datetime(2026, 11, 7)
    for g in games:
        g["days_ago"] = (max_date - g["dt"]).days

    return team_meta, games


def evaluate_walk_forward(
    team_meta,
    all_games,
    ridge_alpha=15.0,
    recency_decay=1.0,
    margin_cap=0.0,
    three_pt_luck_weight=0.0,
    altitude_boost=False,
    min_train_games=1100,   # Start testing around Dec 10 once teams have ~6 games
    step_games=250,         # Re-fit every ~4 days of games across the season
):
    """
    Walk-forward out-of-sample evaluation across the season.
    For each chunk [idx : idx + step_games], train strictly on all_games[:idx]
    (recomputing days_ago relative to the split date!) and predict the test chunk.
    """
    abs_errors = []
    sq_errors = []
    correct_picks = 0
    total_non_tie = 0
    log_losses = []

    # Precompute cumulative team tempos dynamically during walk-forward
    for split_idx in range(min_train_games, len(all_games), step_games):
        train_slice = all_games[:split_idx]
        test_slice = all_games[split_idx : split_idx + step_games]
        if not test_slice:
            break

        split_dt = train_slice[-1]["dt"]
        # Re-index days_ago relative to the current split date (no future leakage!)
        for g in train_slice:
            g["days_ago"] = max(0, (split_dt - g["dt"]).days)

        model = solve_kenpom_ridge(
            team_meta,
            train_slice,
            ridge_alpha=ridge_alpha,
            recency_decay=recency_decay,
            margin_cap=margin_cap,
            three_pt_luck_weight=three_pt_luck_weight,
            altitude_boost=altitude_boost,
        )

        mu = model["national_mean_ortg"]
        hca_tot = model["hca_total_pts_per_100"]
        alt_tot = model["altitude_extra_pts_per_100"]
        team_ratings = {r["team"]: r for r in model["rankings"]}

        # Compute each team's average tempo up to split_dt
        tempo_sum = {}
        tempo_cnt = {}
        for g in train_slice:
            for t in (g["t1"], g["t2"]):
                tempo_sum[t] = tempo_sum.get(t, 0.0) + g["poss"]
                tempo_cnt[t] = tempo_cnt.get(t, 0) + 1

        for g in test_slice:
            t1, t2 = g["t1"], g["t2"]
            if t1 not in team_ratings or t2 not in team_ratings:
                continue
            r1 = team_ratings[t1]
            r2 = team_ratings[t2]

            tempo1 = tempo_sum.get(t1, 68.5) / max(1, tempo_cnt.get(t1, 1))
            tempo2 = tempo_sum.get(t2, 68.5) / max(1, tempo_cnt.get(t2, 1))
            est_poss = 0.5 * (tempo1 + tempo2)

            # Expected efficiency per 100 possessions
            exp_ortg1 = r1["adj_o"] + r2["adj_d"] - mu
            exp_ortg2 = r2["adj_o"] + r1["adj_d"] - mu

            if not g["neutral"]:
                hca_game = hca_tot + (alt_tot if (altitude_boost and t2 in HIGH_ALTITUDE_TEAMS) else 0.0)
                exp_ortg2 += 0.5 * hca_game
                exp_ortg1 -= 0.5 * hca_game

            pred_margin_t2 = (exp_ortg2 - exp_ortg1) * (est_poss / 100.0)
            actual_margin_t2 = g["t2_pts"] - g["t1_pts"]

            err = pred_margin_t2 - actual_margin_t2
            abs_errors.append(abs(err))
            sq_errors.append(err * err)

            if actual_margin_t2 != 0:
                total_non_tie += 1
                if (pred_margin_t2 > 0 and actual_margin_t2 > 0) or (pred_margin_t2 < 0 and actual_margin_t2 < 0):
                    correct_picks += 1

                # Win probability via normal CDF (sigma = 11.0 pts)
                z = pred_margin_t2 / 11.0
                prob_t2 = 1.0 / (1.0 + math.exp(-1.702 * z))
                prob_t2 = min(max(prob_t2, 1e-5), 1.0 - 1e-5)
                y_true = 1.0 if actual_margin_t2 > 0 else 0.0
                ll = -(y_true * math.log(prob_t2) + (1.0 - y_true) * math.log(1.0 - prob_t2))
                log_losses.append(ll)

    return {
        "n_test_games": len(abs_errors),
        "mae": round(float(np.mean(abs_errors)), 3),
        "rmse": round(float(math.sqrt(np.mean(sq_errors))), 3),
        "win_acc_pct": round(100.0 * correct_picks / max(1, total_non_tie), 2),
        "log_loss": round(float(np.mean(log_losses)), 4),
    }


def solve_early_season_with_priors(
    team_meta_27,
    games_27,
    prior_rankings_26,
    prior_weight=18.0,      # Strength of preseason prior (equivalent to ~6-8 games)
    prior_shrinkage=0.65,   # Regress last year's ratings 35% toward national average
):
    """
    Solves the live 2026-27 season (currently 258 D-I games played through Nov 7, 2026)
    by combining actual 2026-27 box scores with a Bayesian Ridge Prior from 2025-26.
    Mathematically:
       (X^T W X + lambda * I) x = X^T W y + lambda * x_prior
    As a team plays more games in 2026-27, X^T W X grows and naturally overwhelms lambda * x_prior!
    """
    teams = sorted(team_meta_27.keys())
    team_idx = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    n_params = 2 * n_teams + 1
    hca_idx = 2 * n_teams

    # Map 2025-26 final offensive and defensive deltas
    mu_26 = np.mean([r["adj_o"] for r in prior_rankings_26])
    prior_map = {r["team"]: r for r in prior_rankings_26}

    x_prior = np.zeros(n_params, dtype=np.float64)
    for i, t in enumerate(teams):
        if t in prior_map:
            x_prior[i] = prior_shrinkage * (prior_map[t]["adj_o"] - mu_26)
            x_prior[n_teams + i] = prior_shrinkage * (prior_map[t]["adj_d"] - mu_26)
    x_prior[hca_idx] = 2.0  # +4.0 pts/100 poss prior HCA

    A = np.zeros((n_params, n_params), dtype=np.float64)
    b = np.zeros(n_params, dtype=np.float64)

    # Compute 2026-27 national mean efficiency
    if games_27:
        mu_27 = float(np.mean([100.0 * (g["t1_pts"] + g["t2_pts"]) / (2.0 * g["poss"]) for g in games_27]))
    else:
        mu_27 = 108.0

    games_played = {t: 0 for t in teams}
    for g in games_27:
        t1, t2 = g["t1"], g["t2"]
        poss = g["poss"]
        ortg1 = 100.0 * g["t1_pts"] / poss
        ortg2 = 100.0 * g["t2_pts"] / poss

        # Cap early-season blowouts at 24 pts/100
        diff = ortg1 - ortg2
        if abs(diff) > 24.0:
            mid = 0.5 * (ortg1 + ortg2)
            capped = math.copysign(24.0 + 0.25 * (abs(diff) - 24.0), diff)
            ortg1 = mid + 0.5 * capped
            ortg2 = mid - 0.5 * capped

        i1, i2 = team_idx[t1], team_idx[t2]
        games_played[t1] += 1
        games_played[t2] += 1

        # Obs 1: Away Offense vs Home Defense
        y1 = ortg1 - mu_27
        idx1 = [(i1, 1.0), (n_teams + i2, 1.0)]
        if not g["neutral"]:
            idx1.append((hca_idx, -1.0))
        for r_i, r_v in idx1:
            b[r_i] += r_v * y1
            for c_i, c_v in idx1:
                A[r_i, c_i] += r_v * c_v

        # Obs 2: Home Offense vs Away Defense
        y2 = ortg2 - mu_27
        idx2 = [(i2, 1.0), (n_teams + i1, 1.0)]
        if not g["neutral"]:
            idx2.append((hca_idx, 1.0))
        for r_i, r_v in idx2:
            b[r_i] += r_v * y2
            for c_i, c_v in idx2:
                A[r_i, c_i] += r_v * c_v

    # Add Bayesian Prior penalty: A += lambda * I, b += lambda * x_prior
    for i in range(2 * n_teams):
        A[i, i] += prior_weight
        b[i] += prior_weight * x_prior[i]
    A[hca_idx, hca_idx] += 5.0
    b[hca_idx] += 5.0 * x_prior[hca_idx]

    sol = np.linalg.solve(A, b)
    off_d = sol[:n_teams] - np.mean(sol[:n_teams])
    def_d = sol[n_teams : 2 * n_teams] - np.mean(sol[n_teams : 2 * n_teams])

    rankings = []
    for i, t in enumerate(teams):
        adj_o = mu_27 + off_d[i]
        adj_d = mu_27 + def_d[i]
        adj_em = adj_o - adj_d
        prior_em = (x_prior[i] - x_prior[n_teams + i])
        rankings.append({
            "team": t,
            "conf": team_meta_27[t]["conf"],
            "record": team_meta_27[t]["record"],
            "games_played": games_played[t],
            "adj_em": round(adj_em, 2),
            "adj_o": round(adj_o, 2),
            "adj_d": round(adj_d, 2),
            "em_change_from_prior": round(adj_em - prior_em, 2),
            "torvik_live_rank": team_meta_27[t]["torvik_rank"],
        })

    rankings.sort(key=lambda x: x["adj_em"], reverse=True)
    for idx, r in enumerate(rankings, 1):
        r["rank"] = idx

    return rankings


if __name__ == "__main__":
    print("1. Running Walk-Forward Out-of-Sample Backtest on 2025-26 Season (4,652 test games)...")
    meta_26, games_26 = load_season_games(2026)

    configs = [
        ("Raw OLS (Unregularized, No Twists)", {"ridge_alpha": 0.5, "recency_decay": 1.0, "margin_cap": 0.0, "three_pt_luck_weight": 0.0, "altitude_boost": False}),
        ("Pure KenPom Baseline (Ridge λ=15)", {"ridge_alpha": 15.0, "recency_decay": 1.0, "margin_cap": 0.0, "three_pt_luck_weight": 0.0, "altitude_boost": False}),
        ("+ Blowout Margin Cap (22 pts/100)", {"ridge_alpha": 15.0, "recency_decay": 1.0, "margin_cap": 22.0, "three_pt_luck_weight": 0.0, "altitude_boost": False}),
        ("+ Recency Decay (0.995/day)", {"ridge_alpha": 15.0, "recency_decay": 0.995, "margin_cap": 22.0, "three_pt_luck_weight": 0.0, "altitude_boost": False}),
        ("+ High-Altitude HCA Bonus", {"ridge_alpha": 15.0, "recency_decay": 0.995, "margin_cap": 22.0, "three_pt_luck_weight": 0.0, "altitude_boost": True}),
        ("Full Custom Twist (+20% 3PT Luck Reg.)", {"ridge_alpha": 15.0, "recency_decay": 0.995, "margin_cap": 22.0, "three_pt_luck_weight": 0.20, "altitude_boost": True}),
        ("Over-Aggressive 3PT Luck (80% Reg.)", {"ridge_alpha": 15.0, "recency_decay": 0.995, "margin_cap": 22.0, "three_pt_luck_weight": 0.80, "altitude_boost": True}),
    ]

    print(f"\n{'Model Configuration':<40} | {'Win Acc%':>8} | {'Spread MAE':>10} | {'RMSE':>7} | {'LogLoss':>8}")
    print("-" * 83)
    backtest_results = []
    for label, params in configs:
        res = evaluate_walk_forward(meta_26, games_26, **params)
        backtest_results.append({"label": label, "params": params, **res})
        print(f"{label:<40} | {res['win_acc_pct']:>7.2f}% | {res['mae']:>7.3f} pt | {res['rmse']:>7.3f} | {res['log_loss']:>8.4f}")

    print("\n2. Solving LIVE 2026-27 Season (through Nov 7, 2026) with Bayesian Prior Updating...")
    base_26 = solve_kenpom_ridge(meta_26, games_26, ridge_alpha=15.0, margin_cap=22.0)
    meta_27, games_27 = load_season_games(2027)
    live_27 = solve_early_season_with_priors(meta_27, games_27, base_26["rankings"])

    print(f"Loaded {len(games_27)} completed D-I vs D-I games in 2026-27 (Opening Week through Nov 7, 2026).")
    print(f"\n{'Rk':<4} {'Team':<20} {'Conf':<5} {'26-27 Rec':<10} {'AdjEM':>7} {'AdjO':>6} {'AdjD':>6} {'vs Prior':>9} {'Torvik27#':>10}")
    print("-" * 84)
    for r in live_27[:15]:
        print(f"{r['rank']:<4} {r['team']:<20} {r['conf']:<5} {r['record']:<10} {r['adj_em']:>+7.2f} {r['adj_o']:>6.1f} {r['adj_d']:>6.1f} {r['em_change_from_prior']:>+9.2f} {r['torvik_live_rank']:>10}")
