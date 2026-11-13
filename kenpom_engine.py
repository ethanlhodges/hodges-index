#!/usr/bin/env python3
"""
Unified College Basketball Ranking Engine (KenPom-style + Backtest-Validated Twists)
-----------------------------------------------------------------------------------
Single source of truth for:
- PRODUCTION_CONFIG (locked-in hyperparameters)
- Data loading (load_season_games, load_priors)
- Vectorized Weighted Ridge Regression for:
    1. Adjusted Offensive & Defensive Efficiency (AdjO, AdjD, AdjEM)
    2. Ridge-Adjusted Tempo (AdjTempo)
    3. Empirical Bayes 3P% Shrinkage (Beta-Binomial prior toward 34.0%)
    4. Possession-Weighted Observations & Four Factors
    5. Anchored Home Court Advantage + High-Altitude Venue Bonus
    6. Dynamic Decaying Preseason Priors (with -15.0 AdjEM default for new D-I teams)
"""

import json
import math
from datetime import datetime
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent

HIGH_ALTITUDE_TEAMS = {
    "Wyoming", "Air Force", "Colorado St.", "Colorado", "Denver",
    "Utah St.", "BYU", "Utah", "Utah Valley", "Weber St.", "Southern Utah",
    "Utah Tech", "New Mexico", "New Mexico St.", "Northern Arizona",
    "Idaho St.", "Montana St.", "Montana", "Boise St.", "Nevada", "UNLV",
}

PRODUCTION_CONFIG = {
    "zero_ridge_alpha": 1.5,
    "recency_decay": 0.9975,
    "margin_cap": 35.0,
    "three_pt_luck_weight": 0.15,
    "eb_3p_prior_att": 150.0,
    "eb_3p_prior_mean": 0.340,
    "altitude_boost": True,
    "prior_max_weight": 7.5,
    "prior_fadeout_games": 14.0,
    "prior_shrinkage": 0.90,
    "new_d1_prior_off": -7.5,   # -15.0 AdjEM default for newly transitioned D-I teams
    "new_d1_prior_def": 7.5,
    "hca_prior_per_side": 2.0,  # +4.0 pts/100 poss total HCA prior
    "hca_prior_weight": 10.0,
    "alt_prior_per_side": 0.775,
    "alt_prior_weight": 4.0,
    "prob_sigma": 10.5,
    "std_hca": 4.0,
    "alt_hca": 1.55,
}


def load_season_games(year_prefix: int):
    """Load D-I vs D-I completed games and team metadata for a Torvik season file."""
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
            "t1_tov": float(box[16]),  # Index 16 is TOV in Torvik box array
            "t2_fga": float(box[20]),
            "t2_fgm": float(box[19]),
            "t2_fta": float(box[24]),
            "t2_orb": float(box[25]),
            "t2_drb": float(box[26]),
            "t2_tov": float(box[31]),  # Index 31 is TOV in Torvik box array
        })

    games.sort(key=lambda x: x["dt"])
    max_date = max(dates) if dates else datetime.now()
    for g in games:
        g["days_ago"] = (max_date - g["dt"]).days

    return team_meta, games


def load_priors_from_team_results(year_prefix: int):
    """Load final ratings from a prior season's team_results.json."""
    with open(DATA_DIR / f"{year_prefix}_team_results.json", "r") as f:
        raw = json.load(f)
    mean_o = float(np.mean([float(r[4]) for r in raw]))
    mean_d = float(np.mean([float(r[6]) for r in raw]))
    return {r[1]: (float(r[4]) - mean_o, float(r[6]) - mean_d) for r in raw}


def solve_model(
    team_meta,
    games,
    priors_map=None,
    prior_weight=0.0,
    prior_shrinkage=0.55,
    zero_ridge_alpha=1.5,
    recency_decay=0.9975,
    margin_cap=35.0,
    three_pt_luck_weight=0.15,
    eb_3p_prior_att=150.0,
    eb_3p_prior_mean=0.340,
    altitude_boost=True,
    possession_weighted=True,
    ref_date=None,
):
    """
    Vectorized Weighted Ridge Regression solver for:
      - AdjO, AdjD, AdjEM
      - Ridge-Adjusted Tempo (AdjTempo)
      - Possession-weighted Four Factors (eFG%, TOV%, ORB%, Opp ORB%)
    """
    teams = sorted(team_meta.keys())
    team_idx = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    n_games = len(games)

    if n_games == 0:
        raise ValueError("No completed games provided to solve_model.")

    # Vectorized extraction of game arrays
    i1 = np.array([team_idx[g["t1"]] for g in games], dtype=np.int32)
    i2 = np.array([team_idx[g["t2"]] for g in games], dtype=np.int32)
    is_neutral = np.array([g["neutral"] for g in games], dtype=bool)
    poss = np.array([g["poss"] for g in games], dtype=np.float64)
    pts1 = np.array([g["t1_pts"] for g in games], dtype=np.float64)
    pts2 = np.array([g["t2_pts"] for g in games], dtype=np.float64)
    m3_1 = np.array([g["t1_3pm"] for g in games], dtype=np.float64)
    a3_1 = np.array([g["t1_3pa"] for g in games], dtype=np.float64)
    m3_2 = np.array([g["t2_3pm"] for g in games], dtype=np.float64)
    a3_2 = np.array([g["t2_3pa"] for g in games], dtype=np.float64)

    if ref_date is not None:
        days_ago = np.array([max(0, (ref_date - g["dt"]).days) for g in games], dtype=np.float64)
    else:
        days_ago = np.array([g["days_ago"] for g in games], dtype=np.float64)

    # 1. Empirical Bayes 3P% Shrinkage (Beta-Binomial prior toward 34.0%)
    made_3 = np.zeros(n_teams, dtype=np.float64)
    att_3 = np.zeros(n_teams, dtype=np.float64)
    np.add.at(made_3, i1, m3_1)
    np.add.at(att_3, i1, a3_1)
    np.add.at(made_3, i2, m3_2)
    np.add.at(att_3, i2, a3_2)
    eb_3p = (made_3 + eb_3p_prior_att * eb_3p_prior_mean) / (att_3 + eb_3p_prior_att)

    if three_pt_luck_weight > 0.0:
        pts1 = pts1 + three_pt_luck_weight * 3.0 * (a3_1 * eb_3p[i1] - m3_1)
        pts2 = pts2 + three_pt_luck_weight * 3.0 * (a3_2 * eb_3p[i2] - m3_2)

    ortg1 = 100.0 * pts1 / poss
    ortg2 = 100.0 * pts2 / poss

    # 2. Soft Garbage-Time / Blowout Margin Cap
    if margin_cap > 0.0:
        diff = ortg1 - ortg2
        over = np.abs(diff) > margin_cap
        if np.any(over):
            mid = 0.5 * (ortg1[over] + ortg2[over])
            capped = np.sign(diff[over]) * (margin_cap + 0.25 * (np.abs(diff[over]) - margin_cap))
            ortg1[over] = mid + 0.5 * capped
            ortg2[over] = mid - 0.5 * capped

    # 3. Recency + Possession Weights (normalized to mean 1.0)
    raw_w = (recency_decay ** days_ago)
    if possession_weighted:
        raw_w = raw_w * (poss / 68.5)
    w = raw_w / np.mean(raw_w)

    total_w = 2.0 * np.sum(w)
    mu = float(np.sum(w * (ortg1 + ortg2)) / total_w)

    # 4. Vectorized Normal Equations Assembly for Efficiency (2*N_teams + 2)
    n_params = 2 * n_teams + 2
    hca_idx = 2 * n_teams
    alt_idx = 2 * n_teams + 1

    A = np.zeros((n_params, n_params), dtype=np.float64)
    b = np.zeros(n_params, dtype=np.float64)

    y1 = ortg1 - mu
    y2 = ortg2 - mu

    # Diagonal & off-diagonal contributions from Obs 1 (i1 off vs n_teams+i2 def) and Obs 2 (i2 off vs n_teams+i1 def)
    np.add.at(A, (i1, i1), w)
    np.add.at(A, (n_teams + i2, n_teams + i2), w)
    np.add.at(A, (i1, n_teams + i2), w)
    np.add.at(A, (n_teams + i2, i1), w)
    np.add.at(b, i1, w * y1)
    np.add.at(b, n_teams + i2, w * y1)

    np.add.at(A, (i2, i2), w)
    np.add.at(A, (n_teams + i1, n_teams + i1), w)
    np.add.at(A, (i2, n_teams + i1), w)
    np.add.at(A, (n_teams + i1, i2), w)
    np.add.at(b, i2, w * y2)
    np.add.at(b, n_teams + i1, w * y2)

    # Home Court Advantage terms (non-neutral games)
    home_mask = ~is_neutral
    if np.any(home_mask):
        wh = w[home_mask]
        hi1 = i1[home_mask]
        hi2 = i2[home_mask]
        hy1 = y1[home_mask]
        hy2 = y2[home_mask]

        A[hca_idx, hca_idx] += 2.0 * np.sum(wh)
        b[hca_idx] += np.sum(wh * (hy2 - hy1))

        # Cross terms between HCA and team ratings:
        # Obs 1 has (-1)*hca, Obs 2 has (+1)*hca
        np.add.at(A, (hi1, hca_idx), -wh)
        np.add.at(A, (hca_idx, hi1), -wh)
        np.add.at(A, (n_teams + hi2, hca_idx), -wh)
        np.add.at(A, (hca_idx, n_teams + hi2), -wh)

        np.add.at(A, (hi2, hca_idx), wh)
        np.add.at(A, (hca_idx, hi2), wh)
        np.add.at(A, (n_teams + hi1, hca_idx), wh)
        np.add.at(A, (hca_idx, n_teams + hi1), wh)

        if altitude_boost:
            is_alt_home = home_mask & np.array([g["t2"] in HIGH_ALTITUDE_TEAMS for g in games], dtype=bool)
            if np.any(is_alt_home):
                wa = w[is_alt_home]
                ai1 = i1[is_alt_home]
                ai2 = i2[is_alt_home]
                ay1 = y1[is_alt_home]
                ay2 = y2[is_alt_home]

                A[alt_idx, alt_idx] += 2.0 * np.sum(wa)
                A[hca_idx, alt_idx] += 2.0 * np.sum(wa)
                A[alt_idx, hca_idx] += 2.0 * np.sum(wa)
                b[alt_idx] += np.sum(wa * (ay2 - ay1))

                np.add.at(A, (ai1, alt_idx), -wa)
                np.add.at(A, (alt_idx, ai1), -wa)
                np.add.at(A, (n_teams + ai2, alt_idx), -wa)
                np.add.at(A, (alt_idx, n_teams + ai2), -wa)

                np.add.at(A, (ai2, alt_idx), wa)
                np.add.at(A, (alt_idx, ai2), wa)
                np.add.at(A, (n_teams + ai1, alt_idx), wa)
                np.add.at(A, (alt_idx, n_teams + ai1), wa)

    # Regularization + Bayesian Preseason Prior Target
    tot_reg = zero_ridge_alpha + (prior_weight if priors_map else 0.0)
    idx_teams = np.arange(n_teams)
    A[idx_teams, idx_teams] += tot_reg
    A[n_teams + idx_teams, n_teams + idx_teams] += tot_reg

    if priors_map and prior_weight > 0.0:
        pr_o = np.array([
            prior_shrinkage * priors_map[t][0] if t in priors_map else PRODUCTION_CONFIG["new_d1_prior_off"]
            for t in teams
        ], dtype=np.float64)
        pr_d = np.array([
            prior_shrinkage * priors_map[t][1] if t in priors_map else PRODUCTION_CONFIG["new_d1_prior_def"]
            for t in teams
        ], dtype=np.float64)
        b[:n_teams] += prior_weight * pr_o
        b[n_teams : 2 * n_teams] += prior_weight * pr_d

    # Anchored HCA priors so Week-1 home blowouts don't distort AdjO/AdjD
    hca_pw = PRODUCTION_CONFIG["hca_prior_weight"]
    A[hca_idx, hca_idx] += hca_pw
    b[hca_idx] += hca_pw * PRODUCTION_CONFIG["hca_prior_per_side"]

    alt_pw = PRODUCTION_CONFIG["alt_prior_weight"]
    A[alt_idx, alt_idx] += alt_pw
    if altitude_boost:
        b[alt_idx] += alt_pw * PRODUCTION_CONFIG["alt_prior_per_side"]

    params = np.linalg.solve(A, b)
    off_d = params[:n_teams]
    def_d = params[n_teams : 2 * n_teams]

    # Exact mean-centering: adjust mu by mean_off + mean_def so AdjO + AdjD - mu is invariant
    mean_off = float(np.mean(off_d))
    mean_def = float(np.mean(def_d))
    off_d = off_d - mean_off
    def_d = def_d - mean_def
    mu_centered = mu + mean_off + mean_def

    # 5. Ridge-Adjusted Tempo (AdjTempo)
    mu_tempo = float(np.sum(w * poss) / np.sum(w))
    yt = poss - mu_tempo
    At = np.zeros((n_teams, n_teams), dtype=np.float64)
    bt = np.zeros(n_teams, dtype=np.float64)
    np.add.at(At, (i1, i1), w)
    np.add.at(At, (i2, i2), w)
    np.add.at(At, (i1, i2), w)
    np.add.at(At, (i2, i1), w)
    np.add.at(bt, i1, w * yt)
    np.add.at(bt, i2, w * yt)
    At[idx_teams, idx_teams] += 6.0  # Tempo shrinkage prior
    tempo_deltas = np.linalg.solve(At, bt)
    tempo_deltas -= np.mean(tempo_deltas)
    adj_tempo = mu_tempo + 0.5 * tempo_deltas  # Each team contributes half of game tempo delta

    # 6. Possession-Weighted Four Factors
    fgm1 = np.array([g["t1_fgm"] for g in games], dtype=np.float64)
    fga1 = np.array([g["t1_fga"] for g in games], dtype=np.float64)
    fgm2 = np.array([g["t2_fgm"] for g in games], dtype=np.float64)
    fga2 = np.array([g["t2_fga"] for g in games], dtype=np.float64)
    orb1 = np.array([g["t1_orb"] for g in games], dtype=np.float64)
    drb1 = np.array([g["t1_drb"] for g in games], dtype=np.float64)
    orb2 = np.array([g["t2_orb"] for g in games], dtype=np.float64)
    drb2 = np.array([g["t2_drb"] for g in games], dtype=np.float64)
    tov1 = np.array([g["t1_tov"] for g in games], dtype=np.float64)
    tov2 = np.array([g["t2_tov"] for g in games], dtype=np.float64)

    tot_fga = np.zeros(n_teams)
    tot_efg_num = np.zeros(n_teams)
    tot_orb = np.zeros(n_teams)
    tot_orb_opp = np.zeros(n_teams)
    tot_drb_allow = np.zeros(n_teams)
    tot_drb_opp = np.zeros(n_teams)
    tot_tov = np.zeros(n_teams)
    tot_poss = np.zeros(n_teams)
    g_cnt = np.zeros(n_teams, dtype=np.int32)

    np.add.at(tot_fga, i1, fga1); np.add.at(tot_fga, i2, fga2)
    np.add.at(tot_efg_num, i1, fgm1 + 0.5 * m3_1); np.add.at(tot_efg_num, i2, fgm2 + 0.5 * m3_2)
    np.add.at(tot_orb, i1, orb1); np.add.at(tot_orb, i2, orb2)
    np.add.at(tot_orb_opp, i1, orb1 + drb2); np.add.at(tot_orb_opp, i2, orb2 + drb1)
    np.add.at(tot_drb_allow, i1, orb2); np.add.at(tot_drb_allow, i2, orb1)
    np.add.at(tot_drb_opp, i1, orb2 + drb1); np.add.at(tot_drb_opp, i2, orb1 + drb2)
    np.add.at(tot_tov, i1, tov1); np.add.at(tot_tov, i2, tov2)
    np.add.at(tot_poss, i1, poss); np.add.at(tot_poss, i2, poss)
    np.add.at(g_cnt, i1, 1); np.add.at(g_cnt, i2, 1)

    team_stats = {}
    rankings = []
    for i, t in enumerate(teams):
        adj_o = float(mu_centered + off_d[i])
        adj_d = float(mu_centered + def_d[i])
        adj_em = adj_o - adj_d
        t_tempo = float(adj_tempo[i]) if g_cnt[i] > 0 else mu_tempo
        efg = float(tot_efg_num[i] / tot_fga[i]) if tot_fga[i] > 0 else 0.51
        orb_r = float(tot_orb[i] / tot_orb_opp[i]) if tot_orb_opp[i] > 0 else 0.30
        drb_a = float(tot_drb_allow[i] / tot_drb_opp[i]) if tot_drb_opp[i] > 0 else 0.30
        tov_r = float(tot_tov[i] / tot_poss[i]) if tot_poss[i] > 0 else 0.17

        st = {
            "team": t,
            "conf": team_meta[t]["conf"],
            "record": team_meta[t]["record"],
            "gp": int(g_cnt[i]),
            "adj_o": adj_o,
            "adj_d": adj_d,
            "adj_em": adj_em,
            "tempo": t_tempo,
            "efg": efg,
            "orb_rate": orb_r,
            "drb_allow": drb_a,
            "tov_rate": tov_r,
            "eb_3p": float(eb_3p[i]),
            "torvik_rank": team_meta[t]["torvik_rank"],
        }
        team_stats[t] = st
        rankings.append(st)

    rankings.sort(key=lambda x: x["adj_em"], reverse=True)
    for rk, r in enumerate(rankings, 1):
        r["rank"] = rk

    return {
        "mu": mu_centered,
        "mu_tempo": mu_tempo,
        "hca_tot": float(2.0 * params[hca_idx]),
        "alt_tot": float(2.0 * params[alt_idx]),
        "teams": team_stats,
        "rankings": rankings,
    }
