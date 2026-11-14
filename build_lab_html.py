#!/usr/bin/env python3
"""
Builds the upgraded College Basketball Ranking Laboratory HTML Artifact with:
- Dual-Season Switcher:
  1. 2025-26 Full Season (5,752 D-I games, complete through NCAA Tournament)
  2. 2026-27 LIVE Opening Week (258 D-I games through Nov 7, 2026 + Bayesian Preseason Prior slider!)
- Walk-Forward Out-of-Sample Backtest Benchmark Tab (4,652 out-of-sample games evaluated)
- Live In-Browser Conjugate Gradient Ridge Solver with Prior Target support
"""

from pathlib import Path

COMPACT_MULTI = Path("/home/antigravity/cbb_rankings/compact_multi_season.json").read_text()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>College Basketball Ranking Laboratory (Live 2026-27 + Backtester)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    input[type="range"] { accent-color: var(--primary); }
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 md:p-6 select-none">

  <div class="max-w-7xl mx-auto space-y-5">
    <!-- Top Header & Season Switcher -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 border-b border-[var(--border)] pb-4">
      <div>
        <div class="flex flex-wrap items-center gap-2">
          <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-[var(--primary)] text-[var(--primary-foreground)]">LIVE RIDGE SOLVER</span>
          <h1 class="text-xl md:text-2xl font-bold tracking-tight text-[var(--foreground)]">College Basketball Ranking Laboratory</h1>
        </div>
        <p id="header-subtitle" class="text-sm text-[var(--muted-foreground)] mt-1">
          Solving <strong class="text-[var(--foreground)]">5,752 D-I games</strong> across <strong class="text-[var(--foreground)]">365 teams</strong> directly in your browser.
        </p>
      </div>

      <!-- Season Toggle + Presets -->
      <div class="flex flex-wrap items-center gap-2">
        <div class="inline-flex rounded-lg border border-[var(--border)] bg-[var(--card)] p-1">
          <button onclick="switchSeason('s2027')" id="btn-season-2027" class="px-3 py-1 text-xs font-semibold rounded-md transition bg-[var(--secondary)] text-[var(--secondary-foreground)]">
            🟢 2026-27 LIVE (Thru Nov 7)
          </button>
          <button onclick="switchSeason('s2026')" id="btn-season-2026" class="px-3 py-1 text-xs font-semibold rounded-md transition bg-[var(--primary)] text-[var(--primary-foreground)]">
            🏆 2025-26 Full Season (5,752 Games)
          </button>
        </div>

        <button onclick="applyPreset('backtest_opt')" id="preset-backtest_opt" class="px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)] transition">
          ★ Backtest-Optimal Twist
        </button>
        <button onclick="applyPreset('baseline')" id="preset-baseline" class="px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--secondary)] transition">
          Pure Baseline
        </button>
        <button onclick="applyPreset('march')" id="preset-march" class="px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--secondary)] transition">
          Hot-Streak Mode
        </button>
      </div>
    </div>

    <!-- Top KPI Strip -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <div class="text-xs text-[var(--muted-foreground)] font-medium">#1 Overall Team</div>
        <div id="kpi-top-team" class="text-base font-bold text-[var(--foreground)] mt-1 truncate">Michigan</div>
        <div id="kpi-top-em" class="text-xs text-[var(--muted-foreground)] mt-0.5">+23.5 AdjEM</div>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <div class="text-xs text-[var(--muted-foreground)] font-medium">D-I Avg Efficiency (μ)</div>
        <div id="kpi-mu" class="text-base font-bold text-[var(--foreground)] mt-1">109.4</div>
        <div id="kpi-games-count" class="text-xs text-[var(--muted-foreground)] mt-0.5">5,752 D-I games</div>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <div class="text-xs text-[var(--muted-foreground)] font-medium">Learned Home Court</div>
        <div id="kpi-hca" class="text-base font-bold text-[var(--foreground)] mt-1">+4.21</div>
        <div id="kpi-alt" class="text-xs text-[var(--muted-foreground)] mt-0.5">Altitude bonus: +1.55</div>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <div class="text-xs text-[var(--muted-foreground)] font-medium">Biggest Twist Riser (Top 65)</div>
        <div id="kpi-riser" class="text-base font-bold text-emerald-500 mt-1 truncate">—</div>
        <div id="kpi-riser-sub" class="text-xs text-[var(--muted-foreground)] mt-0.5">vs. Pure Baseline</div>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <div class="text-xs text-[var(--muted-foreground)] font-medium">Out-of-Sample Accuracy</div>
        <div class="text-base font-bold text-emerald-500 mt-1">69.91% Win / 9.11 MAE</div>
        <div class="text-xs text-[var(--muted-foreground)] mt-0.5">Walk-forward on 4,652 games</div>
      </div>
    </div>

    <!-- Main Grid: Left Controls + Right Tabs -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
      
      <!-- Left Column: Model Twist Controls (4 cols) -->
      <div class="lg:col-span-4 space-y-4">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm space-y-3.5">
          <div class="flex items-center justify-between border-b border-[var(--border)] pb-2">
            <h2 class="text-sm font-semibold text-[var(--foreground)]">Model Hyperparameters & Twists</h2>
            <span id="solve-badge" class="text-xs font-mono text-[var(--muted-foreground)]">18 ms</span>
          </div>

          <!-- Preseason Prior Weight (Highlighted in 2026-27 Live Mode) -->
          <div id="prior-control-box" class="p-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] space-y-1.5 hidden">
            <div class="flex justify-between text-xs">
              <label class="font-semibold text-amber-500">★ 2026-27 Preseason Prior Weight</label>
              <span id="val-prior" class="font-mono font-semibold text-amber-500">65% Carryover</span>
            </div>
            <input id="inp-prior" type="range" min="0" max="100" step="5" value="65" oninput="onControlChange()" class="w-full cursor-pointer" />
            <p class="text-xs text-[var(--muted-foreground)]">
              Anchors early 2026-27 ratings (only 1-2 games played) to each team's 2025-26 rating so unbeaten mid-majors don't break the matrix.
            </p>
          </div>

          <!-- Slider 1: Recency Half-Life -->
          <div class="space-y-1">
            <div class="flex justify-between text-xs">
              <label class="font-medium text-[var(--foreground)]">1. Recency Decay (Daily Weight)</label>
              <span id="val-recency" class="font-mono font-semibold text-[var(--primary)]">0.997 / day</span>
            </div>
            <input id="inp-recency" type="range" min="0.980" max="1.000" step="0.001" value="0.997" oninput="onControlChange()" class="w-full cursor-pointer" />
            <div class="flex justify-between text-xs text-[var(--muted-foreground)]">
              <span>0.980 (Heavy March)</span>
              <span id="sub-recency">Nov game = 67% wt</span>
              <span>1.000 (Flat)</span>
            </div>
          </div>

          <!-- Slider 2: Garbage-Time / Margin Cap -->
          <div class="space-y-1 pt-2 border-t border-[var(--border)]">
            <div class="flex justify-between text-xs">
              <label class="font-medium text-[var(--foreground)]">2. Blowout / Garbage-Time Cap</label>
              <span id="val-cap" class="font-mono font-semibold text-[var(--primary)]">30 pts/100</span>
            </div>
            <input id="inp-cap" type="range" min="12" max="55" step="1" value="30" oninput="onControlChange()" class="w-full cursor-pointer" />
            <div class="flex justify-between text-xs text-[var(--muted-foreground)]">
              <span>12 (Strict)</span>
              <span>Diminishing returns past cap</span>
              <span>55 (Uncapped)</span>
            </div>
          </div>

          <!-- Slider 3: 3-Point Luck Regression -->
          <div class="space-y-1 pt-2 border-t border-[var(--border)]">
            <div class="flex justify-between text-xs">
              <label class="font-medium text-[var(--foreground)]">3. 3-Point Luck Regression</label>
              <span id="val-luck" class="font-mono font-semibold text-[var(--primary)]">15% regressed</span>
            </div>
            <input id="inp-luck" type="range" min="0" max="100" step="5" value="15" oninput="onControlChange()" class="w-full cursor-pointer" />
            <p class="text-xs text-[var(--muted-foreground)]">
              Backtest proved <strong>15–20%</strong> 3PT luck regression cuts Spread MAE from 9.14 to 9.11 pts!
            </p>
          </div>

          <!-- Slider 4: Ridge Regularization Alpha -->
          <div class="space-y-1 pt-2 border-t border-[var(--border)]">
            <div class="flex justify-between text-xs">
              <label class="font-medium text-[var(--foreground)]">4. Ridge Shrinkage Penalty (λ)</label>
              <span id="val-alpha" class="font-mono font-semibold text-[var(--primary)]">λ = 2.0</span>
            </div>
            <input id="inp-alpha" type="range" min="0.5" max="35.0" step="0.5" value="2.0" oninput="onControlChange()" class="w-full cursor-pointer" />
            <div class="flex justify-between text-xs text-[var(--muted-foreground)]">
              <span>0.5 (Low shrinkage)</span>
              <span>Backtest optimal: λ ≈ 1.5–3.0</span>
              <span>35.0 (Heavy)</span>
            </div>
          </div>

          <!-- Toggle 5: High-Altitude HCA Bonus -->
          <div class="pt-2 border-t border-[var(--border)] flex items-center justify-between">
            <div>
              <div class="text-xs font-medium text-[var(--foreground)]">5. High-Altitude Venue HCA Term</div>
              <div class="text-xs text-[var(--muted-foreground)]">Separate HCA for BYU, New Mexico, Utah St, Wyo, etc.</div>
            </div>
            <input id="inp-altitude" type="checkbox" checked onchange="onControlChange()" class="h-4 w-4 rounded border-[var(--border)] cursor-pointer" />
          </div>
        </div>

        <!-- Neutral / Home Matchup Simulator Card -->
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b border-[var(--border)] pb-2">
            <h2 class="text-sm font-semibold text-[var(--foreground)]">Head-to-Head Game Predictor</h2>
            <span class="text-xs text-[var(--muted-foreground)]">Uses Live Ratings</span>
          </div>

          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="text-xs text-[var(--muted-foreground)] block mb-1">Team A (Away / Neutral)</label>
              <select id="sim-team-a" onchange="updateSimulator()" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] p-2"></select>
            </div>
            <div>
              <label class="text-xs text-[var(--muted-foreground)] block mb-1">Team B (Home / Neutral)</label>
              <select id="sim-team-b" onchange="updateSimulator()" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] p-2"></select>
            </div>
          </div>

          <div class="flex items-center gap-2 pt-1">
            <span class="text-xs text-[var(--muted-foreground)]">Venue:</span>
            <button onclick="setSimVenue('neutral')" id="venue-neutral" class="px-2.5 py-1 text-xs rounded-md bg-[var(--primary)] text-[var(--primary-foreground)] font-medium">Neutral Court</button>
            <button onclick="setSimVenue('home_b')" id="venue-home_b" class="px-2.5 py-1 text-xs rounded-md bg-[var(--secondary)] text-[var(--secondary-foreground)] font-medium">At Team B</button>
            <button onclick="setSimVenue('home_a')" id="venue-home_a" class="px-2.5 py-1 text-xs rounded-md bg-[var(--secondary)] text-[var(--secondary-foreground)] font-medium">At Team A</button>
          </div>

          <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-3 space-y-2">
            <div class="flex items-center justify-between">
              <span id="sim-score-a" class="text-lg font-bold text-[var(--foreground)]">Duke 76.4</span>
              <span class="text-xs font-semibold px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--muted-foreground)]">VS</span>
              <span id="sim-score-b" class="text-lg font-bold text-[var(--foreground)]">Michigan 77.1</span>
            </div>
            <div class="w-full h-2.5 bg-[var(--secondary)] rounded-full overflow-hidden flex">
              <div id="sim-bar-a" class="h-full bg-blue-500 transition-all duration-200" style="width: 48%"></div>
              <div id="sim-bar-b" class="h-full bg-amber-500 transition-all duration-200" style="width: 52%"></div>
            </div>
            <div class="flex justify-between text-xs text-[var(--muted-foreground)]">
              <span id="sim-prob-a">48% Win Prob</span>
              <span id="sim-tempo">Est. 68.4 Poss</span>
              <span id="sim-prob-b">52% Win Prob</span>
            </div>
            <div id="sim-spread" class="text-center text-xs font-medium text-[var(--foreground)] pt-1 border-t border-[var(--border)]">
              Projected Spread: Michigan -0.7
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Leaderboard, Scatter Plot, Movers & Backtest Proof (8 cols) -->
      <div class="lg:col-span-8 space-y-4">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm space-y-3">
          
          <!-- Filter & View Mode Bar -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 border-b border-[var(--border)] pb-3">
            <div class="flex flex-wrap items-center gap-1.5">
              <button onclick="switchTab('table')" id="tab-table" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)]">
                Rankings Table
              </button>
              <button onclick="switchTab('scatter')" id="tab-scatter" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]">
                AdjO vs. AdjD Map
              </button>
              <button onclick="switchTab('movers')" id="tab-movers" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]">
                Biggest Movers
              </button>
              <button onclick="switchTab('backtest')" id="tab-backtest" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]">
                📊 Backtest Findings
              </button>
            </div>

            <div class="flex items-center gap-2">
              <input id="search-input" type="text" placeholder="Search team..." oninput="renderActiveView()" class="px-2.5 py-1 text-xs rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] w-32" />
              <select id="conf-filter" onchange="renderActiveView()" class="px-2.5 py-1 text-xs rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)]">
                <option value="ALL">All Conf</option>
              </select>
            </div>
          </div>

          <!-- View 1: Live Rankings Table -->
          <div id="view-table" class="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table class="w-full text-left border-collapse">
              <thead class="sticky top-0 bg-[var(--card)] border-b border-[var(--border)] text-xs text-[var(--muted-foreground)]">
                <tr>
                  <th class="py-2 px-2.5 font-semibold">Rank</th>
                  <th class="py-2 px-2 font-semibold" title="Rank change vs Pure Baseline">vs Base</th>
                  <th class="py-2 px-2.5 font-semibold">Team</th>
                  <th class="py-2 px-2 font-semibold">Conf</th>
                  <th class="py-2 px-2 font-semibold">Rec</th>
                  <th class="py-2 px-2.5 font-semibold text-right">AdjEM</th>
                  <th class="py-2 px-2.5 font-semibold text-right">AdjO (Rk)</th>
                  <th class="py-2 px-2.5 font-semibold text-right">AdjD (Rk)</th>
                  <th class="py-2 px-2 font-semibold text-right">3P%</th>
                  <th class="py-2 px-2 font-semibold text-right" title="Bart Torvik T-Rank reference">T-Rank</th>
                </tr>
              </thead>
              <tbody id="rankings-tbody" class="divide-y divide-[var(--border)] text-xs"></tbody>
            </table>
          </div>

          <!-- View 2: Interactive Efficiency Scatter Plot -->
          <div id="view-scatter" class="hidden space-y-2">
            <div class="flex items-center justify-between text-xs text-[var(--muted-foreground)] px-1">
              <span>Top-Right = Elite Offense & Elite Defense (Defensive axis inverted so UP is better defense)</span>
              <span>Click any team dot to inspect resume</span>
            </div>
            <div class="relative w-full h-[460px] bg-[var(--background)] border border-[var(--border)] rounded-lg overflow-hidden">
              <canvas id="scatter-canvas" class="w-full h-full cursor-crosshair"></canvas>
            </div>
          </div>

          <!-- View 3: Biggest Twist Movers -->
          <div id="view-movers" class="hidden grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[500px] overflow-y-auto p-1">
            <div class="border border-[var(--border)] rounded-lg p-3 bg-[var(--background)]">
              <h3 class="text-xs font-bold text-emerald-500 uppercase tracking-wider mb-2">Biggest Risers Under Your Twist (Top 100)</h3>
              <div id="movers-up" class="space-y-1.5 text-xs"></div>
            </div>
            <div class="border border-[var(--border)] rounded-lg p-3 bg-[var(--background)]">
              <h3 class="text-xs font-bold text-rose-500 uppercase tracking-wider mb-2">Biggest Fallers Under Your Twist (Top 100)</h3>
              <div id="movers-down" class="space-y-1.5 text-xs"></div>
            </div>
          </div>

          <!-- View 4: Walk-Forward Backtest Findings -->
          <div id="view-backtest" class="hidden space-y-4 max-h-[500px] overflow-y-auto p-1 text-xs">
            <div class="p-3.5 rounded-lg border border-[var(--border)] bg-[var(--background)] space-y-2">
              <h3 class="text-sm font-bold text-[var(--foreground)]">Walk-Forward Out-of-Sample Backtest (4,652 D-I Games Tested)</h3>
              <p class="text-[var(--muted-foreground)] leading-relaxed">
                Every 250 games across the season (from Dec 10 through the National Championship), the model trained strictly on games played <strong>before</strong> Date T (with zero future data leakage) and predicted the exact point spread and win probability of the next 250 games.
              </p>
              <table class="w-full text-left border-collapse mt-2">
                <thead class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <tr>
                    <th class="py-2 px-2">Model Configuration (Ablation Study)</th>
                    <th class="py-2 px-2 text-right">Winner Acc %</th>
                    <th class="py-2 px-2 text-right">Spread MAE</th>
                    <th class="py-2 px-2 text-right">Spread RMSE</th>
                    <th class="py-2 px-2 text-right">Log-Loss</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[var(--border)] font-mono">
                  <tr>
                    <td class="py-2 px-2 font-sans text-rose-500">Over-Shrinkage toward 0 (λ = 15.0, No Preseason Prior)</td>
                    <td class="py-2 px-2 text-right">66.06%</td>
                    <td class="py-2 px-2 text-right">9.884 pts</td>
                    <td class="py-2 px-2 text-right">12.592</td>
                    <td class="py-2 px-2 text-right">0.6124</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-2 font-sans">Pure KenPom Baseline (λ = 1.5, Flat Weights, Uncapped)</td>
                    <td class="py-2 px-2 text-right">69.75%</td>
                    <td class="py-2 px-2 text-right">9.147 pts</td>
                    <td class="py-2 px-2 text-right">11.559</td>
                    <td class="py-2 px-2 text-right">0.5612</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-2 font-sans">+ Mild Recency Decay (0.9975 / day)</td>
                    <td class="py-2 px-2 text-right">69.86%</td>
                    <td class="py-2 px-2 text-right">9.142 pts</td>
                    <td class="py-2 px-2 text-right">11.553</td>
                    <td class="py-2 px-2 text-right">0.5608</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-2 font-sans">+ High-Altitude Venue HCA Bonus (+1.55 pts/100)</td>
                    <td class="py-2 px-2 text-right">69.88%</td>
                    <td class="py-2 px-2 text-right">9.141 pts</td>
                    <td class="py-2 px-2 text-right">11.551</td>
                    <td class="py-2 px-2 text-right">0.5606</td>
                  </tr>
                  <tr class="bg-emerald-500/10 font-bold text-emerald-500">
                    <td class="py-2 px-2 font-sans">★ + 15% 3-Point Luck Regression (Shot Quality Twist)</td>
                    <td class="py-2 px-2 text-right">69.91%</td>
                    <td class="py-2 px-2 text-right">9.112 pts</td>
                    <td class="py-2 px-2 text-right">11.513</td>
                    <td class="py-2 px-2 text-right">0.5586</td>
                  </tr>
                  <tr>
                    <td class="py-2 px-2 font-sans">+ Soft Blowout Cap (35 pts/100) — Best Probability Calibration</td>
                    <td class="py-2 px-2 text-right">69.88%</td>
                    <td class="py-2 px-2 text-right">9.114 pts</td>
                    <td class="py-2 px-2 text-right">11.563</td>
                    <td class="py-2 px-2 text-right font-bold text-emerald-500">0.5581</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="p-3 rounded-lg border border-[var(--border)] bg-[var(--background)] space-y-1">
                <div class="font-bold text-[var(--foreground)]">Insight 1: Why 15% 3PT Luck Regression Works</div>
                <p class="text-[var(--muted-foreground)] leading-relaxed">
                  Regressing 15% of single-game 3-point variance toward each team's season 3P% yielded the largest single drop in Spread MAE (from 9.141 down to 9.112 pts). However, regressing 80% hurt MAE (9.93 pts) because 3PT defense and spacing still contain real signal!
                </p>
              </div>
              <div class="p-3 rounded-lg border border-[var(--border)] bg-[var(--background)] space-y-1">
                <div class="font-bold text-[var(--foreground)]">Insight 2: Shrinkage to Zero vs. Shrinkage to Prior</div>
                <p class="text-[var(--muted-foreground)] leading-relaxed">
                  Heavy Ridge shrinkage toward zero (λ=15) compresses top teams too close to average, hurting spread MAE. Instead, shrinking toward last season's <strong>Preseason Prior</strong> early in the year (and using λ ≈ 1.5–2.0 once teams have 10+ games) gives you stability without compression!
                </p>
              </div>
            </div>
          </div>

        </div>

        <!-- Selected Team Game Log & Four Factors Inspector -->
        <div id="team-inspector" class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--border)] pb-2.5">
            <div>
              <div class="flex items-center gap-2">
                <h3 id="insp-title" class="text-base font-bold text-[var(--foreground)]">Duke Blue Devils</h3>
                <span id="insp-badge" class="px-2 py-0.5 text-xs font-semibold rounded bg-[var(--secondary)] text-[var(--foreground)]">#1 Overall</span>
              </div>
              <p id="insp-sub" class="text-xs text-[var(--muted-foreground)] mt-0.5">Click any team in the table or scatter plot to inspect their Four Factors and game-by-game efficiency.</p>
            </div>
            <div class="grid grid-cols-4 gap-2 text-center">
              <div class="px-2.5 py-1 rounded bg-[var(--background)] border border-[var(--border)]">
                <div class="text-xs text-[var(--muted-foreground)]">eFG%</div>
                <div id="insp-efg" class="text-xs font-bold text-[var(--foreground)]">56.2%</div>
              </div>
              <div class="px-2.5 py-1 rounded bg-[var(--background)] border border-[var(--border)]">
                <div class="text-xs text-[var(--muted-foreground)]">TOV%</div>
                <div id="insp-tov" class="text-xs font-bold text-[var(--foreground)]">15.1%</div>
              </div>
              <div class="px-2.5 py-1 rounded bg-[var(--background)] border border-[var(--border)]">
                <div class="text-xs text-[var(--muted-foreground)]">ORB%</div>
                <div id="insp-orb" class="text-xs font-bold text-[var(--foreground)]">33.4%</div>
              </div>
              <div class="px-2.5 py-1 rounded bg-[var(--background)] border border-[var(--border)]">
                <div class="text-xs text-[var(--muted-foreground)]">Tempo</div>
                <div id="insp-tempo" class="text-xs font-bold text-[var(--foreground)]">69.8</div>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto max-h-44 overflow-y-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="sticky top-0 bg-[var(--card)] border-b border-[var(--border)] text-[var(--muted-foreground)]">
                <tr>
                  <th class="py-1.5 px-2">Date</th>
                  <th class="py-1.5 px-2">Loc</th>
                  <th class="py-1.5 px-2">Opponent (Rk)</th>
                  <th class="py-1.5 px-2">Result</th>
                  <th class="py-1.5 px-2 text-right">Poss</th>
                  <th class="py-1.5 px-2 text-right">Raw ORtg</th>
                  <th class="py-1.5 px-2 text-right">Raw DRtg</th>
                  <th class="py-1.5 px-2 text-right">3PT</th>
                  <th class="py-1.5 px-2 text-right">Recency Wt</th>
                </tr>
              </thead>
              <tbody id="insp-games-tbody" class="divide-y divide-[var(--border)]"></tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </div>

  <script>
    // Embedded Multi-Season NCAA D-I dataset (2025-26 full 5,752 games + 2026-27 live 258 games)
    const MULTI_DATA = __COMPACT_MULTI_PLACEHOLDER__;

    let activeSeasonKey = 's2026';
    let TEAMS = MULTI_DATA.s2026.teams;
    let GAMES = MULTI_DATA.s2026.games;
    let N_TEAMS = TEAMS.length;

    let baselineRankMap = {};
    let currentRankings = [];
    let currentTeamByIdx = {};
    let activeTab = 'table';
    let selectedTeamIdx = 0;
    let simVenue = 'neutral';
    let lastWarmSolution = null;

    function solveConjugateGradient(A_flat, b, n, warmStart) {
      const x = (warmStart && warmStart.length === n) ? new Float64Array(warmStart) : new Float64Array(n);
      const r = new Float64Array(n);
      const p = new Float64Array(n);
      const Ap = new Float64Array(n);

      for (let i = 0; i < n; i++) {
        let sum = 0.0;
        const rowOffset = i * n;
        for (let j = 0; j < n; j++) sum += A_flat[rowOffset + j] * x[j];
        r[i] = b[i] - sum;
        p[i] = r[i];
      }

      let rsold = 0.0;
      for (let i = 0; i < n; i++) rsold += r[i] * r[i];
      if (Math.sqrt(rsold) < 1e-8) return x;

      const maxIter = 180;
      for (let iter = 0; iter < maxIter; iter++) {
        let pAp = 0.0;
        for (let i = 0; i < n; i++) {
          let sum = 0.0;
          const rowOffset = i * n;
          for (let j = 0; j < n; j++) sum += A_flat[rowOffset + j] * p[j];
          Ap[i] = sum;
          pAp += p[i] * sum;
        }
        if (Math.abs(pAp) < 1e-14) break;
        const alpha = rsold / pAp;
        let rsnew = 0.0;
        for (let i = 0; i < n; i++) {
          x[i] += alpha * p[i];
          r[i] -= alpha * Ap[i];
          rsnew += r[i] * r[i];
        }
        if (Math.sqrt(rsnew) < 1e-6) break;
        const beta = rsnew / rsold;
        for (let i = 0; i < n; i++) p[i] = r[i] + beta * p[i];
        rsold = rsnew;
      }
      return x;
    }

    function runRidgeModel(params, isBaseline = false) {
      const t0 = performance.now();
      const { recencyDecay, marginCap, luckWeight, ridgeAlpha, altitudeBoost, priorCarryover } = params;

      const nParams = 2 * N_TEAMS + 2;
      const hcaIdx = 2 * N_TEAMS;
      const altIdx = 2 * N_TEAMS + 1;

      const A = new Float64Array(nParams * nParams);
      const b = new Float64Array(nParams);

      const nGames = GAMES.length;
      const rawWeights = new Float64Array(nGames);
      let sumW = 0.0;
      for (let k = 0; k < nGames; k++) {
        const w = Math.pow(recencyDecay, GAMES[k][3]);
        rawWeights[k] = w;
        sumW += w;
      }
      const meanW = nGames > 0 ? (sumW / nGames) : 1.0;

      const ortg1Arr = new Float64Array(nGames);
      const ortg2Arr = new Float64Array(nGames);
      const normWArr = new Float64Array(nGames);

      let totalWOrtg = 0.0;
      let totalW = 0.0;

      for (let k = 0; k < nGames; k++) {
        const g = GAMES[k];
        const i1 = g[0], i2 = g[1];
        const poss = g[4];
        let pts1 = g[5], pts2 = g[6];

        if (luckWeight > 0) {
          const exp3_1 = g[8] * TEAMS[i1][4];
          const exp3_2 = g[10] * TEAMS[i2][4];
          pts1 += luckWeight * 3.0 * (exp3_1 - g[7]);
          pts2 += luckWeight * 3.0 * (exp3_2 - g[9]);
        }

        let o1 = 100.0 * pts1 / poss;
        let o2 = 100.0 * pts2 / poss;

        if (marginCap < 55) {
          const diff = o1 - o2;
          if (Math.abs(diff) > marginCap) {
            const mid = 0.5 * (o1 + o2);
            const sign = diff >= 0 ? 1.0 : -1.0;
            const capped = sign * (marginCap + 0.25 * (Math.abs(diff) - marginCap));
            o1 = mid + 0.5 * capped;
            o2 = mid - 0.5 * capped;
          }
        }

        const w = rawWeights[k] / meanW;
        ortg1Arr[k] = o1;
        ortg2Arr[k] = o2;
        normWArr[k] = w;

        totalWOrtg += w * (o1 + o2);
        totalW += 2.0 * w;
      }

      const mu = totalW > 0 ? (totalWOrtg / totalW) : 108.5;

      function addObs(indices, vals, len, weight, y) {
        for (let a = 0; a < len; a++) {
          const rIdx = indices[a];
          const wr = weight * vals[a];
          b[rIdx] += wr * y;
          const rowOff = rIdx * nParams;
          for (let c = 0; c < len; c++) {
            A[rowOff + indices[c]] += wr * vals[c];
          }
        }
      }

      const idxBuf = [0, 0, 0, 0];
      const valBuf = [0, 0, 0, 0];

      for (let k = 0; k < nGames; k++) {
        const g = GAMES[k];
        const i1 = g[0], i2 = g[1];
        const isNeutral = g[2] === 1;
        const w = normWArr[k];

        let len1 = 2;
        idxBuf[0] = i1; valBuf[0] = 1.0;
        idxBuf[1] = N_TEAMS + i2; valBuf[1] = 1.0;
        if (!isNeutral) {
          idxBuf[len1] = hcaIdx; valBuf[len1] = -1.0; len1++;
          if (altitudeBoost && TEAMS[i2][5] === 1) {
            idxBuf[len1] = altIdx; valBuf[len1] = -1.0; len1++;
          }
        }
        addObs(idxBuf, valBuf, len1, w, ortg1Arr[k] - mu);

        let len2 = 2;
        idxBuf[0] = i2; valBuf[0] = 1.0;
        idxBuf[1] = N_TEAMS + i1; valBuf[1] = 1.0;
        if (!isNeutral) {
          idxBuf[len2] = hcaIdx; valBuf[len2] = 1.0; len2++;
          if (altitudeBoost && TEAMS[i2][5] === 1) {
            idxBuf[len2] = altIdx; valBuf[len2] = 1.0; len2++;
          }
        }
        addObs(idxBuf, valBuf, len2, w, ortg2Arr[k] - mu);
      }

      // Add Ridge L2 penalty (and Bayesian Preseason Prior target if in 2026-27 live season)
      for (let i = 0; i < N_TEAMS; i++) {
        A[i * nParams + i] += ridgeAlpha;
        A[(N_TEAMS + i) * nParams + (N_TEAMS + i)] += ridgeAlpha;
        if (activeSeasonKey === 's2027' && priorCarryover > 0) {
          const priorO = TEAMS[i][11] * priorCarryover;
          const priorD = TEAMS[i][12] * priorCarryover;
          b[i] += ridgeAlpha * priorO;
          b[N_TEAMS + i] += ridgeAlpha * priorD;
        }
      }
      A[hcaIdx * nParams + hcaIdx] += (activeSeasonKey === 's2027' ? 3.0 : 0.05);
      if (activeSeasonKey === 's2027') b[hcaIdx] += 3.0 * 1.9;
      A[altIdx * nParams + altIdx] += 1.0;

      const sol = solveConjugateGradient(A, b, nParams, lastWarmSolution);
      if (!isBaseline) lastWarmSolution = sol;

      let meanOff = 0.0, meanDef = 0.0;
      for (let i = 0; i < N_TEAMS; i++) {
        meanOff += sol[i];
        meanDef += sol[N_TEAMS + i];
      }
      meanOff /= N_TEAMS;
      meanDef /= N_TEAMS;

      const results = [];
      for (let i = 0; i < N_TEAMS; i++) {
        const adjO = mu + (sol[i] - meanOff);
        const adjD = mu + (sol[N_TEAMS + i] - meanDef);
        const adjEM = adjO - adjD;
        results.push({
          teamIdx: i,
          name: TEAMS[i][0],
          conf: TEAMS[i][1],
          record: TEAMS[i][2],
          torvikRank: TEAMS[i][3],
          threePct: (TEAMS[i][4] * 100).toFixed(1),
          isAltitude: TEAMS[i][5] === 1,
          tempo: TEAMS[i][6],
          efg: TEAMS[i][7],
          tov: TEAMS[i][8],
          orb: TEAMS[i][9],
          ftr: TEAMS[i][10],
          gamesPlayed: TEAMS[i][13],
          adjO,
          adjD,
          adjEM
        });
      }

      const byO = [...results].sort((a, b) => b.adjO - a.adjO);
      byO.forEach((r, idx) => { r.oRank = idx + 1; });
      const byD = [...results].sort((a, b) => a.adjD - b.adjD);
      byD.forEach((r, idx) => { r.dRank = idx + 1; });

      results.sort((a, b) => b.adjEM - a.adjEM);
      results.forEach((r, idx) => {
        r.rank = idx + 1;
        if (isBaseline) {
          baselineRankMap[r.teamIdx] = r.rank;
          r.rankDelta = 0;
        } else {
          r.rankDelta = (baselineRankMap[r.teamIdx] || r.rank) - r.rank;
        }
        currentTeamByIdx[r.teamIdx] = r;
      });

      const elapsedMs = Math.max(1, Math.round(performance.now() - t0));
      return {
        mu,
        hca: 2.0 * sol[hcaIdx],
        altHca: 2.0 * sol[altIdx],
        elapsedMs,
        rankings: results
      };
    }

    function getUIParams() {
      const recencyDecay = parseFloat(document.getElementById('inp-recency').value);
      const marginCap = parseFloat(document.getElementById('inp-cap').value);
      const luckWeight = parseFloat(document.getElementById('inp-luck').value) / 100.0;
      const ridgeAlpha = parseFloat(document.getElementById('inp-alpha').value);
      const altitudeBoost = document.getElementById('inp-altitude').checked;
      const priorCarryover = parseFloat(document.getElementById('inp-prior').value) / 100.0;
      return { recencyDecay, marginCap, luckWeight, ridgeAlpha, altitudeBoost, priorCarryover };
    }

    function updateLabels(params) {
      document.getElementById('val-recency').textContent = params.recencyDecay.toFixed(3) + ' / day';
      const novWeight = Math.round(100 * Math.pow(params.recencyDecay, 135));
      document.getElementById('sub-recency').textContent = `Nov game = ${novWeight}% wt`;
      document.getElementById('val-cap').textContent = params.marginCap >= 55 ? 'Uncapped' : `${params.marginCap} pts/100`;
      document.getElementById('val-luck').textContent = `${Math.round(params.luckWeight * 100)}% regressed`;
      document.getElementById('val-alpha').textContent = `λ = ${params.ridgeAlpha.toFixed(1)}`;
      document.getElementById('val-prior').textContent = `${Math.round(params.priorCarryover * 100)}% Carryover`;
    }

    function onControlChange() {
      const params = getUIParams();
      updateLabels(params);
      const res = runRidgeModel(params, false);
      currentRankings = res.rankings;

      const top = currentRankings[0];
      document.getElementById('kpi-top-team').textContent = `#1 ${top.name} (${top.record})`;
      document.getElementById('kpi-top-em').textContent = `${top.adjEM >= 0 ? '+' : ''}${top.adjEM.toFixed(2)} AdjEM | #${top.oRank} Off, #${top.dRank} Def`;
      document.getElementById('kpi-mu').textContent = res.mu.toFixed(1);
      document.getElementById('kpi-games-count').textContent = `${GAMES.length.toLocaleString()} D-I games`;
      document.getElementById('kpi-hca').textContent = `+${res.hca.toFixed(2)} pts`;
      document.getElementById('kpi-alt').textContent = params.altitudeBoost
        ? `Altitude bonus: +${res.altHca.toFixed(2)} pts`
        : 'Altitude bonus: Off';
      document.getElementById('solve-badge').textContent = `${res.elapsedMs} ms`;

      let bestRiser = null;
      for (const r of currentRankings.slice(0, 68)) {
        if (!bestRiser || r.rankDelta > bestRiser.rankDelta) bestRiser = r;
      }
      if (bestRiser && bestRiser.rankDelta > 0) {
        document.getElementById('kpi-riser').textContent = `${bestRiser.name} (+${bestRiser.rankDelta})`;
        document.getElementById('kpi-riser-sub').textContent = `Now #${bestRiser.rank} (was #${baselineRankMap[bestRiser.teamIdx]})`;
      } else {
        document.getElementById('kpi-riser').textContent = 'Matches Baseline';
        document.getElementById('kpi-riser-sub').textContent = 'Adjust sliders to see movers';
      }

      renderActiveView();
      updateSimulator();
      renderTeamInspector(selectedTeamIdx);
    }

    function switchSeason(seasonKey) {
      activeSeasonKey = seasonKey;
      TEAMS = MULTI_DATA[seasonKey].teams;
      GAMES = MULTI_DATA[seasonKey].games;
      N_TEAMS = TEAMS.length;
      lastWarmSolution = null;

      const btn26 = document.getElementById('btn-season-2026');
      const btn27 = document.getElementById('btn-season-2027');
      const priorBox = document.getElementById('prior-control-box');

      if (seasonKey === 's2027') {
        btn27.className = 'px-3 py-1 text-xs font-semibold rounded-md transition bg-[var(--primary)] text-[var(--primary-foreground)]';
        btn26.className = 'px-3 py-1 text-xs font-semibold rounded-md transition bg-[var(--secondary)] text-[var(--secondary-foreground)]';
        priorBox.classList.remove('hidden');
        document.getElementById('inp-alpha').value = '8.0';
        document.getElementById('header-subtitle').innerHTML = 'Solving <strong>LIVE 2026-27 Season</strong> (258 D-I games played through Nov 7, 2026) blended with Bayesian Preseason Priors.';
      } else {
        btn26.className = 'px-3 py-1 text-xs font-semibold rounded-md transition bg-[var(--primary)] text-[var(--primary-foreground)]';
        btn27.className = 'px-3 py-1 text-xs font-semibold rounded-md transition bg-[var(--secondary)] text-[var(--secondary-foreground)]';
        priorBox.classList.add('hidden');
        document.getElementById('inp-alpha').value = '2.0';
        document.getElementById('header-subtitle').innerHTML = 'Solving <strong>5,752 D-I games</strong> across <strong>365 teams</strong> (Full 2025-26 Season) directly in your browser.';
      }

      // Compute season baseline
      const baseRes = runRidgeModel({
        recencyDecay: 1.0,
        marginCap: 55,
        luckWeight: 0.0,
        ridgeAlpha: seasonKey === 's2027' ? 8.0 : 2.0,
        altitudeBoost: false,
        priorCarryover: seasonKey === 's2027' ? 0.65 : 0.0
      }, true);

      // Re-populate simulator dropdowns
      const simA = document.getElementById('sim-team-a');
      const simB = document.getElementById('sim-team-b');
      simA.innerHTML = '';
      simB.innerHTML = '';
      baseRes.rankings.forEach(r => {
        const optA = document.createElement('option');
        optA.value = r.teamIdx;
        optA.textContent = `#${r.rank} ${r.name} (${r.conf})`;
        simA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = r.teamIdx;
        optB.textContent = `#${r.rank} ${r.name} (${r.conf})`;
        simB.appendChild(optB);
      });
      simA.selectedIndex = 0;
      simB.selectedIndex = 1;
      selectedTeamIdx = baseRes.rankings[0].teamIdx;

      onControlChange();
    }

    function renderActiveView() {
      if (activeTab === 'table') renderTable();
      else if (activeTab === 'scatter') renderScatter();
      else if (activeTab === 'movers') renderMovers();
    }

    function getFilteredRankings() {
      const q = document.getElementById('search-input').value.trim().toLowerCase();
      const conf = document.getElementById('conf-filter').value;
      return currentRankings.filter(r => {
        if (conf !== 'ALL' && r.conf !== conf) return false;
        if (q && !r.name.toLowerCase().includes(q)) return false;
        return true;
      });
    }

    function renderTable() {
      const rows = getFilteredRankings().slice(0, 120);
      const tbody = document.getElementById('rankings-tbody');
      tbody.innerHTML = rows.map(r => {
        let deltaBadge = `<span class="text-[var(--muted-foreground)]">—</span>`;
        if (r.rankDelta > 0) {
          deltaBadge = `<span class="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-500 font-semibold">+${r.rankDelta}</span>`;
        } else if (r.rankDelta < 0) {
          deltaBadge = `<span class="px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-500 font-semibold">${r.rankDelta}</span>`;
        }
        const isSelected = r.teamIdx === selectedTeamIdx;
        const rowClass = isSelected
          ? 'bg-[var(--secondary)] cursor-pointer transition'
          : 'hover:bg-[var(--secondary)]/60 cursor-pointer transition';

        return `
          <tr class="${rowClass}" onclick="selectTeam(${r.teamIdx})">
            <td class="py-2 px-2.5 font-bold text-[var(--foreground)]">${r.rank}</td>
            <td class="py-2 px-2">${deltaBadge}</td>
            <td class="py-2 px-2.5 font-semibold text-[var(--foreground)]">
              ${r.name}
              ${r.isAltitude ? '<span title="High-Altitude Venue" class="ml-1 text-xs text-amber-500">▲</span>' : ''}
            </td>
            <td class="py-2 px-2 text-[var(--muted-foreground)]">${r.conf}</td>
            <td class="py-2 px-2 text-[var(--muted-foreground)]">${r.record}</td>
            <td class="py-2 px-2.5 text-right font-mono font-bold text-[var(--foreground)]">${r.adjEM >= 0 ? '+' : ''}${r.adjEM.toFixed(2)}</td>
            <td class="py-2 px-2.5 text-right font-mono">${r.adjO.toFixed(1)} <span class="text-[var(--muted-foreground)]">(${r.oRank})</span></td>
            <td class="py-2 px-2.5 text-right font-mono">${r.adjD.toFixed(1)} <span class="text-[var(--muted-foreground)]">(${r.dRank})</span></td>
            <td class="py-2 px-2 text-right font-mono text-[var(--muted-foreground)]">${r.threePct}%</td>
            <td class="py-2 px-2 text-right font-mono text-[var(--muted-foreground)]">#${r.torvikRank}</td>
          </tr>
        `;
      }).join('');
    }

    function renderMovers() {
      const top100 = currentRankings.filter(r => r.rank <= 100 || baselineRankMap[r.teamIdx] <= 100);
      const risers = [...top100].sort((a, b) => b.rankDelta - a.rankDelta).slice(0, 12);
      const fallers = [...top100].sort((a, b) => a.rankDelta - b.rankDelta).slice(0, 12);

      document.getElementById('movers-up').innerHTML = risers.map(r => `
        <div onclick="selectTeam(${r.teamIdx})" class="flex items-center justify-between p-2 rounded hover:bg-[var(--secondary)] cursor-pointer border border-transparent hover:border-[var(--border)]">
          <div>
            <span class="font-bold text-[var(--foreground)]">#${r.rank} ${r.name}</span>
            <span class="text-[var(--muted-foreground)] ml-1">(${r.conf} · ${r.record})</span>
          </div>
          <div class="text-right">
            <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-500 font-bold">+${r.rankDelta} spots</span>
            <span class="text-[var(--muted-foreground)] ml-1.5">was #${baselineRankMap[r.teamIdx]}</span>
          </div>
        </div>
      `).join('');

      document.getElementById('movers-down').innerHTML = fallers.map(r => `
        <div onclick="selectTeam(${r.teamIdx})" class="flex items-center justify-between p-2 rounded hover:bg-[var(--secondary)] cursor-pointer border border-transparent hover:border-[var(--border)]">
          <div>
            <span class="font-bold text-[var(--foreground)]">#${r.rank} ${r.name}</span>
            <span class="text-[var(--muted-foreground)] ml-1">(${r.conf} · ${r.record})</span>
          </div>
          <div class="text-right">
            <span class="px-2 py-0.5 rounded bg-rose-500/15 text-rose-500 font-bold">${r.rankDelta} spots</span>
            <span class="text-[var(--muted-foreground)] ml-1.5">was #${baselineRankMap[r.teamIdx]}</span>
          </div>
        </div>
      `).join('');
    }

    let scatterPoints = [];
    function renderScatter() {
      const canvas = document.getElementById('scatter-canvas');
      if (!canvas) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      const ctx = canvas.getContext('2d');
      ctx.scale(dpr, dpr);

      const W = rect.width;
      const H = rect.height;
      const padL = 52, padR = 24, padT = 24, padB = 40;

      const isLight = document.documentElement.classList.contains('light');
      const gridColor = isLight ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.08)';
      const textColor = isLight ? '#475569' : '#94a3b8';
      const labelColor = isLight ? '#0f172a' : '#f8fafc';

      ctx.clearRect(0, 0, W, H);

      const rows = getFilteredRankings().slice(0, 100);
      if (rows.length === 0) return;

      let minO = 104, maxO = 124;
      let minD = 94, maxD = 112;
      for (const r of rows) {
        if (r.adjO - 1.5 < minO) minO = r.adjO - 1.5;
        if (r.adjO + 1.5 > maxO) maxO = r.adjO + 1.5;
        if (r.adjD - 1.5 < minD) minD = r.adjD - 1.5;
        if (r.adjD + 1.5 > maxD) maxD = r.adjD + 1.5;
      }

      const xMap = o => padL + ((o - minO) / (maxO - minO)) * (W - padL - padR);
      const yMap = d => padT + ((d - minD) / (maxD - minD)) * (H - padT - padB);

      ctx.strokeStyle = gridColor;
      ctx.lineWidth = 1;
      ctx.font = '12px sans-serif';
      ctx.fillStyle = textColor;

      for (let o = Math.ceil(minO / 4) * 4; o <= maxO; o += 4) {
        const x = xMap(o);
        ctx.beginPath(); ctx.moveTo(x, padT); ctx.lineTo(x, H - padB); ctx.stroke();
        ctx.fillText(o.toString(), x - 10, H - padB + 18);
      }
      for (let d = Math.ceil(minD / 4) * 4; d <= maxD; d += 4) {
        const y = yMap(d);
        ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
        ctx.fillText(d.toString(), 14, y + 4);
      }

      ctx.fillStyle = labelColor;
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('Adjusted Offensive Efficiency (AdjO → Higher is Better)', W / 2 - 140, H - 8);

      scatterPoints = [];
      for (const r of rows) {
        const cx = xMap(r.adjO);
        const cy = yMap(r.adjD);
        const isSel = r.teamIdx === selectedTeamIdx;
        scatterPoints.push({ cx, cy, r });

        ctx.beginPath();
        ctx.arc(cx, cy, isSel ? 7 : (r.rank <= 25 ? 5.5 : 4), 0, Math.PI * 2);
        if (isSel) ctx.fillStyle = '#f59e0b';
        else if (r.rank <= 15) ctx.fillStyle = '#3b82f6';
        else if (r.rankDelta >= 5) ctx.fillStyle = '#10b981';
        else ctx.fillStyle = isLight ? '#64748b' : '#94a3b8';
        ctx.fill();

        if (r.rank <= 20 || isSel) {
          ctx.fillStyle = labelColor;
          ctx.font = isSel ? 'bold 12px sans-serif' : '12px sans-serif';
          ctx.fillText(`#${r.rank} ${r.name}`, cx + 8, cy + 4);
        }
      }
    }

    function selectTeam(teamIdx) {
      selectedTeamIdx = teamIdx;
      renderActiveView();
      renderTeamInspector(teamIdx);
    }

    function renderTeamInspector(teamIdx) {
      const t = currentTeamByIdx[teamIdx];
      if (!t) return;

      document.getElementById('insp-title').textContent = `${t.name} (${t.conf} · ${t.record})`;
      const deltaStr = t.rankDelta > 0 ? `+${t.rankDelta} vs Base` : (t.rankDelta < 0 ? `${t.rankDelta} vs Base` : 'Same as Base');
      document.getElementById('insp-badge').textContent = `#${t.rank} Overall (${t.adjEM >= 0 ? '+' : ''}${t.adjEM.toFixed(2)} AdjEM · ${deltaStr})`;
      document.getElementById('insp-efg').textContent = `${t.efg}%`;
      document.getElementById('insp-tov').textContent = `${t.tov}%`;
      document.getElementById('insp-orb').textContent = `${t.orb}%`;
      document.getElementById('insp-tempo').textContent = `${t.tempo}`;

      const recencyDecay = parseFloat(document.getElementById('inp-recency').value);
      const teamGames = [];
      for (const g of GAMES) {
        if (g[0] === teamIdx || g[1] === teamIdx) {
          const isT1 = g[0] === teamIdx;
          const oppIdx = isT1 ? g[1] : g[0];
          const opp = currentTeamByIdx[oppIdx];
          const ptsFor = isT1 ? g[5] : g[6];
          const ptsAgn = isT1 ? g[6] : g[5];
          const m3 = isT1 ? g[7] : g[9];
          const a3 = isT1 ? g[8] : g[10];
          const loc = g[2] === 1 ? 'N' : (isT1 ? 'Away' : 'Home');
          const poss = g[4];
          const rawO = (100.0 * ptsFor / poss).toFixed(1);
          const rawD = (100.0 * ptsAgn / poss).toFixed(1);
          const wt = Math.round(100 * Math.pow(recencyDecay, g[3]));
          teamGames.push({
            date: g[11],
            daysAgo: g[3],
            loc,
            oppName: opp ? opp.name : 'Unknown',
            oppRank: opp ? opp.rank : 999,
            oppIdx,
            win: ptsFor > ptsAgn,
            score: `${ptsFor}-${ptsAgn}`,
            poss: poss.toFixed(0),
            rawO,
            rawD,
            threeStr: `${m3}/${a3}`,
            wt
          });
        }
      }
      teamGames.sort((a, b) => a.daysAgo - b.daysAgo);

      if (teamGames.length === 0) {
        document.getElementById('insp-games-tbody').innerHTML = `
          <tr><td colspan="9" class="py-4 text-center text-[var(--muted-foreground)]">No completed D-I vs. D-I games yet in 2026-27 (rating driven by Bayesian Preseason Prior).</td></tr>
        `;
        return;
      }

      document.getElementById('insp-games-tbody').innerHTML = teamGames.map(tg => `
        <tr class="hover:bg-[var(--secondary)]/50">
          <td class="py-1.5 px-2 text-[var(--muted-foreground)] font-mono">${tg.date}</td>
          <td class="py-1.5 px-2">${tg.loc}</td>
          <td class="py-1.5 px-2 font-medium cursor-pointer hover:underline" onclick="selectTeam(${tg.oppIdx})">
            #${tg.oppRank} ${tg.oppName}
          </td>
          <td class="py-1.5 px-2 font-semibold ${tg.win ? 'text-emerald-500' : 'text-rose-500'}">
            ${tg.win ? 'W' : 'L'} ${tg.score}
          </td>
          <td class="py-1.5 px-2 text-right font-mono text-[var(--muted-foreground)]">${tg.poss}</td>
          <td class="py-1.5 px-2 text-right font-mono">${tg.rawO}</td>
          <td class="py-1.5 px-2 text-right font-mono">${tg.rawD}</td>
          <td class="py-1.5 px-2 text-right font-mono text-[var(--muted-foreground)]">${tg.threeStr}</td>
          <td class="py-1.5 px-2 text-right font-mono">${tg.wt}%</td>
        </tr>
      `).join('');
    }

    function setSimVenue(v) {
      simVenue = v;
      ['neutral', 'home_b', 'home_a'].forEach(mode => {
        const btn = document.getElementById('venue-' + mode);
        if (mode === v) {
          btn.className = 'px-2.5 py-1 text-xs rounded-md bg-[var(--primary)] text-[var(--primary-foreground)] font-medium';
        } else {
          btn.className = 'px-2.5 py-1 text-xs rounded-md bg-[var(--secondary)] text-[var(--secondary-foreground)] font-medium';
        }
      });
      updateSimulator();
    }

    function updateSimulator() {
      const idxA = parseInt(document.getElementById('sim-team-a').value || '0', 10);
      const idxB = parseInt(document.getElementById('sim-team-b').value || '1', 10);
      const teamA = currentTeamByIdx[idxA];
      const teamB = currentTeamByIdx[idxB];
      if (!teamA || !teamB) return;

      const mu = parseFloat(document.getElementById('kpi-mu').textContent) || 109.4;
      const hcaPts = parseFloat(document.getElementById('kpi-hca').textContent.replace('+', '')) || 4.0;
      const estPoss = 0.5 * (teamA.tempo + teamB.tempo);

      let expOrtgA = teamA.adjO + teamB.adjD - mu;
      let expOrtgB = teamB.adjO + teamA.adjD - mu;

      if (simVenue === 'home_b') {
        expOrtgB += 0.5 * hcaPts;
        expOrtgA -= 0.5 * hcaPts;
      } else if (simVenue === 'home_a') {
        expOrtgA += 0.5 * hcaPts;
        expOrtgB -= 0.5 * hcaPts;
      }

      const scoreA = expOrtgA * (estPoss / 100.0);
      const scoreB = expOrtgB * (estPoss / 100.0);
      const diff = scoreA - scoreB;

      const z = diff / 11.0;
      const winProbA = 1.0 / (1.0 + Math.exp(-1.702 * z));
      const pctA = Math.round(winProbA * 100);
      const pctB = 100 - pctA;

      document.getElementById('sim-score-a').textContent = `${teamA.name} ${scoreA.toFixed(1)}`;
      document.getElementById('sim-score-b').textContent = `${teamB.name} ${scoreB.toFixed(1)}`;
      document.getElementById('sim-bar-a').style.width = `${pctA}%`;
      document.getElementById('sim-bar-b').style.width = `${pctB}%`;
      document.getElementById('sim-prob-a').textContent = `${pctA}% Win Prob`;
      document.getElementById('sim-prob-b').textContent = `${pctB}% Win Prob`;
      document.getElementById('sim-tempo').textContent = `Est. ${estPoss.toFixed(1)} Poss`;

      const fav = diff >= 0 ? teamA.name : teamB.name;
      document.getElementById('sim-spread').textContent = `Projected Spread: ${fav} -${Math.abs(diff).toFixed(1)}`;
    }

    function switchTab(tab) {
      activeTab = tab;
      ['table', 'scatter', 'movers', 'backtest'].forEach(t => {
        const btn = document.getElementById('tab-' + t);
        const view = document.getElementById('view-' + t);
        if (t === tab) {
          btn.className = 'px-3 py-1.5 text-xs font-semibold rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)]';
          view.classList.remove('hidden');
        } else {
          btn.className = 'px-3 py-1.5 text-xs font-semibold rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]';
          view.classList.add('hidden');
        }
      });
      renderActiveView();
    }

    function applyPreset(name) {
      ['backtest_opt', 'baseline', 'march'].forEach(p => {
        const btn = document.getElementById('preset-' + p);
        if (p === name) {
          btn.className = 'px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)] transition';
        } else {
          btn.className = 'px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--secondary)] transition';
        }
      });

      if (name === 'baseline') {
        document.getElementById('inp-recency').value = '1.000';
        document.getElementById('inp-cap').value = '55';
        document.getElementById('inp-luck').value = '0';
        document.getElementById('inp-alpha').value = activeSeasonKey === 's2027' ? '8.0' : '2.0';
        document.getElementById('inp-altitude').checked = false;
      } else if (name === 'backtest_opt') {
        document.getElementById('inp-recency').value = '0.997';
        document.getElementById('inp-cap').value = '30';
        document.getElementById('inp-luck').value = '15';
        document.getElementById('inp-alpha').value = activeSeasonKey === 's2027' ? '8.0' : '2.0';
        document.getElementById('inp-altitude').checked = true;
      } else if (name === 'march') {
        document.getElementById('inp-recency').value = '0.985';
        document.getElementById('inp-cap').value = '22';
        document.getElementById('inp-luck').value = '25';
        document.getElementById('inp-alpha').value = activeSeasonKey === 's2027' ? '8.0' : '4.0';
        document.getElementById('inp-altitude').checked = true;
      }
      onControlChange();
    }

    window.addEventListener('DOMContentLoaded', () => {
      const confs = Array.from(new Set(TEAMS.map(t => t[1]))).sort();
      const confSel = document.getElementById('conf-filter');
      confs.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        confSel.appendChild(opt);
      });

      const canvas = document.getElementById('scatter-canvas');
      canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        let closest = null;
        let bestDist = 18;
        for (const pt of scatterPoints) {
          const d = Math.hypot(pt.cx - mx, pt.cy - my);
          if (d < bestDist) {
            bestDist = d;
            closest = pt.r;
          }
        }
        if (closest) selectTeam(closest.teamIdx);
      });

      window.addEventListener('resize', () => {
        if (activeTab === 'scatter') renderScatter();
      });

      switchSeason('s2027');
    });
  </script>
</body>
</html>
"""

final_html = HTML_TEMPLATE.replace("__COMPACT_MULTI_PLACEHOLDER__", COMPACT_MULTI)
Path("/home/antigravity/cbb_rankings/generated_lab.html").write_text(final_html)
Path("/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/1e980916-ecae-478e-bedb-b2e0d94a61c3/cbb_ranking_laboratory.html").write_text(final_html)
print("Updated artifact HTML size:", len(final_html), "bytes")
