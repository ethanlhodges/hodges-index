#!/usr/bin/env python3
"""
Renders HodgesIndex (index.html, generated_site.html, and artifact copies)
with a standalone, rock-solid Light & Dark theme system (no transparent
modals or undefined CSS variables on GitHub Pages!), basketball-inspired
accents, rank-tier pills, visual efficiency bars, and a user-friendly + fun UI.
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent
PAYLOAD_JSON = (DATA_DIR / "site_payload.json").read_text()
ARTIFACT_DIR = Path("/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/1e980916-ecae-478e-bedb-b2e0d94a61c3")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HodgesIndex · 2026–27 D-I College Basketball Ratings</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Standalone solid color tokens that work identically on GitHub Pages and in-app */
    html.light {
      --hi-bg: #f8fafc;
      --hi-surface: #ffffff;
      --hi-surface-alt: #f1f5f9;
      --hi-surface-hover: #fff7ed;
      --hi-border: #e2e8f0;
      --hi-text: #0f172a;
      --hi-muted: #64748b;
      --hi-accent: #ea580c;
      --hi-accent-soft: #ffedd5;
      --hi-accent-text: #9a3412;
      --hi-pos: #059669;
      --hi-neg: #e11d48;
      --hi-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
      --hi-modal-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.35);
    }
    html.dark {
      --hi-bg: #0b0f19;
      --hi-surface: #111827;
      --hi-surface-alt: #1e293b;
      --hi-surface-hover: #1f2937;
      --hi-border: #1f2937;
      --hi-text: #f8fafc;
      --hi-muted: #94a3b8;
      --hi-accent: #f97316;
      --hi-accent-soft: rgba(249, 115, 22, 0.15);
      --hi-accent-text: #fdba74;
      --hi-pos: #10b981;
      --hi-neg: #f43f5e;
      --hi-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
      --hi-modal-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75);
    }

    body {
      background-color: var(--hi-bg);
      color: var(--hi-text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
    }
    .hi-card {
      background-color: var(--hi-surface);
      border: 1px solid var(--hi-border);
      box-shadow: var(--hi-shadow);
    }
    .hi-modal-card {
      background-color: var(--hi-surface);
      border: 1px solid var(--hi-border);
      box-shadow: var(--hi-modal-shadow);
    }
    .hi-subcard {
      background-color: var(--hi-surface-alt);
      border: 1px solid var(--hi-border);
    }
    .hi-input {
      background-color: var(--hi-surface);
      border: 1px solid var(--hi-border);
      color: var(--hi-text);
    }
    .hi-input:focus {
      outline: 2px solid var(--hi-accent);
      outline-offset: -1px;
    }
    .hi-row {
      border-bottom: 1px solid var(--hi-border);
      transition: background-color 0.12s ease;
    }
    .hi-row:hover {
      background-color: var(--hi-surface-hover);
    }
    .tabular-nums { font-variant-numeric: tabular-nums; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--hi-border); border-radius: 3px; }
  </style>
</head>
<body class="antialiased min-h-screen p-4 md:p-8">

  <div class="max-w-6xl mx-auto space-y-6">

    <!-- Top Brand Header -->
    <header class="hi-card rounded-2xl p-4 md:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl flex items-center justify-center text-2xl shadow-xs" style="background: linear-gradient(135deg, #ea580c, #f97316); color: white;">
          🏀
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl md:text-2xl font-extrabold tracking-tight">HodgesIndex</h1>
            <span class="text-xs font-bold px-2 py-0.5 rounded-full" style="background-color: var(--hi-accent-soft); color: var(--hi-accent-text);">
              2026–27 LIVE
            </span>
          </div>
          <p class="text-xs mt-0.5" style="color: var(--hi-muted);">
            Updated <strong id="hdr-date" style="color: var(--hi-text);">—</strong> ·
            <span id="hdr-games">—</span> D-I games ·
            Prior weight: <span id="hdr-prior" class="font-mono font-semibold" style="color: var(--hi-text);">—</span>
          </p>
        </div>
      </div>

      <!-- Navigation Pills + Theme Toggle -->
      <div class="flex flex-wrap items-center gap-2">
        <nav class="inline-flex rounded-xl p-1" style="background-color: var(--hi-surface-alt); border: 1px solid var(--hi-border);">
          <button onclick="switchMainTab('rankings')" id="nav-rankings" class="px-3.5 py-1.5 text-xs font-bold rounded-lg transition">
            🏆 Rankings
          </button>
          <button onclick="switchMainTab('slate')" id="nav-slate" class="px-3.5 py-1.5 text-xs font-bold rounded-lg transition">
            📅 Games Slate
          </button>
          <button onclick="switchMainTab('matchup')" id="nav-matchup" class="px-3.5 py-1.5 text-xs font-bold rounded-lg transition">
            ⚔️ Predictor
          </button>
          <button onclick="switchMainTab('model')" id="nav-model" class="px-3.5 py-1.5 text-xs font-bold rounded-lg transition">
            📐 Methodology
          </button>
        </nav>

        <button onclick="toggleTheme()" id="theme-btn" title="Switch Light / Dark Mode"
          class="px-3 py-2 text-xs font-semibold rounded-xl hi-subcard hover:opacity-80 transition cursor-pointer">
          🌙 Dark
        </button>
      </div>
    </header>

    <!-- Fun Season Pulse Strip -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="hi-card rounded-xl p-3.5 flex items-center justify-between cursor-pointer hover:opacity-95 transition" onclick="openTopCard('no1')">
        <div>
          <div class="text-xs font-medium" style="color: var(--hi-muted);">👑 #1 Overall</div>
          <div id="pulse-no1" class="text-sm md:text-base font-extrabold mt-0.5">—</div>
          <div id="pulse-no1-sub" class="text-xs font-mono font-semibold mt-0.5" style="color: var(--hi-pos);">—</div>
        </div>
      </div>
      <div class="hi-card rounded-xl p-3.5 flex items-center justify-between cursor-pointer hover:opacity-95 transition" onclick="openTopCard('off1')">
        <div>
          <div class="text-xs font-medium" style="color: var(--hi-muted);">🔥 #1 Offense (AdjO)</div>
          <div id="pulse-off1" class="text-sm md:text-base font-extrabold mt-0.5">—</div>
          <div id="pulse-off1-sub" class="text-xs font-mono mt-0.5" style="color: var(--hi-muted);">—</div>
        </div>
      </div>
      <div class="hi-card rounded-xl p-3.5 flex items-center justify-between cursor-pointer hover:opacity-95 transition" onclick="openTopCard('def1')">
        <div>
          <div class="text-xs font-medium" style="color: var(--hi-muted);">🛡️ #1 Defense (AdjD)</div>
          <div id="pulse-def1" class="text-sm md:text-base font-extrabold mt-0.5">—</div>
          <div id="pulse-def1-sub" class="text-xs font-mono mt-0.5" style="color: var(--hi-muted);">—</div>
        </div>
      </div>
      <div class="hi-card rounded-xl p-3.5 flex items-center justify-between cursor-pointer hover:opacity-95 transition" onclick="openTopCard('mover1')">
        <div>
          <div class="text-xs font-medium" style="color: var(--hi-muted);">🚀 Hottest Start vs Prior</div>
          <div id="pulse-mover" class="text-sm md:text-base font-extrabold mt-0.5" style="color: var(--hi-pos);">—</div>
          <div id="pulse-mover-sub" class="text-xs font-mono mt-0.5" style="color: var(--hi-muted);">—</div>
        </div>
      </div>
    </div>

    <!-- ==================== TAB 1: FULL-WIDTH RANKINGS ==================== -->
    <section id="tab-rankings" class="space-y-3.5">
      <!-- Controls Bar -->
      <div class="hi-card rounded-xl p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2.5">
          <input id="rank-search" type="text" placeholder="🔍 Search team (e.g. Duke, Virginia)..." oninput="renderRankingsTable()"
            class="hi-input px-3 py-1.5 text-xs rounded-lg w-56" />
          <select id="rank-conf" onchange="renderRankingsTable()" class="hi-input px-2.5 py-1.5 text-xs rounded-lg cursor-pointer">
            <option value="ALL">All Conferences</option>
          </select>
          <select id="rank-sort" onchange="renderRankingsTable()" class="hi-input px-2.5 py-1.5 text-xs rounded-lg cursor-pointer">
            <option value="adj_em">Sort: Overall (AdjEM)</option>
            <option value="adj_o">Sort: Best Offense (AdjO)</option>
            <option value="adj_d">Sort: Best Defense (AdjD)</option>
            <option value="tempo">Sort: Fastest Pace (AdjT)</option>
          </select>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <label class="inline-flex items-center gap-2 text-xs font-semibold cursor-pointer select-none px-2.5 py-1.5 rounded-lg hi-subcard">
            <input id="toggle-prior" type="checkbox" checked onchange="onTogglePrior()" class="rounded accent-orange-600 cursor-pointer" />
            <span>Include prior-season weighting</span>
          </label>
          <span id="rank-count-label" class="text-xs" style="color: var(--hi-muted);">Click any team for resume</span>
        </div>
      </div>

      <!-- Leaderboard Table -->
      <div class="hi-card rounded-2xl overflow-hidden">
        <div class="overflow-x-auto max-h-[640px] overflow-y-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 text-xs uppercase tracking-wider" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
              <tr>
                <th class="py-3 px-4 font-bold w-14">Rk</th>
                <th class="py-3 px-4 font-bold">Team</th>
                <th class="py-3 px-3 font-bold">Conf</th>
                <th class="py-3 px-3 font-bold">Rec</th>
                <th class="py-3 px-4 font-bold text-right" title="Adjusted Efficiency Margin (Pts/100 poss vs average D-I opponent)">AdjEM</th>
                <th class="py-3 px-4 font-bold text-right" title="Adjusted Offensive Efficiency (Pts scored per 100 poss)">AdjO (Rk)</th>
                <th class="py-3 px-4 font-bold text-right" title="Adjusted Defensive Efficiency (Pts allowed per 100 poss — lower is better)">AdjD (Rk)</th>
                <th class="py-3 px-4 font-bold text-right" title="Adjusted Tempo (Possessions per 40 min)">AdjT</th>
              </tr>
            </thead>
            <tbody id="rankings-tbody" class="text-sm"></tbody>
          </table>
        </div>
        <div class="px-4 py-2.5 text-xs flex flex-wrap items-center justify-between gap-2" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-top: 1px solid var(--hi-border);">
          <span><strong style="color: #d97706;">⛰️ ALT</strong> = High-Altitude Home Venue (+1.55 pts/100 poss elevation boost)</span>
          <span>Click any row to open full game log & Four Factors</span>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 2: DAILY GAMES SLATE ==================== -->
    <section id="tab-slate" class="hidden space-y-4">
      <div class="hi-card rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div id="slate-filter-btns" class="flex flex-wrap items-center gap-2"></div>
        <label class="inline-flex items-center gap-2 text-xs font-semibold cursor-pointer px-2.5 py-1.5 rounded-lg hi-subcard">
          <input id="slate-featured-only" type="checkbox" checked onchange="renderSlate()" class="rounded accent-orange-600 cursor-pointer" />
          <span>Featured matchups only (Top 60 teams)</span>
        </label>
      </div>

      <div class="hi-card rounded-2xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="text-xs uppercase tracking-wider" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
              <tr>
                <th class="py-3 px-4 font-bold">Date</th>
                <th class="py-3 px-4 font-bold">Matchup</th>
                <th class="py-3 px-4 font-bold text-right">Projected Score</th>
                <th class="py-3 px-4 font-bold text-right">HodgesIndex Line</th>
                <th class="py-3 px-4 font-bold text-right">Win Prob</th>
                <th class="py-3 px-4 font-bold text-right">Status / Result</th>
              </tr>
            </thead>
            <tbody id="slate-tbody" class="text-sm"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 3: HEAD-TO-HEAD PREDICTOR ==================== -->
    <section id="tab-matchup" class="hidden max-w-2xl mx-auto space-y-5 pt-2">
      <div class="hi-card rounded-2xl p-6 space-y-5">
        <div class="flex items-center justify-between border-b pb-3" style="border-color: var(--hi-border);">
          <div>
            <h2 class="text-base font-extrabold">⚔️ Head-to-Head Matchup Simulator</h2>
            <p class="text-xs mt-0.5" style="color: var(--hi-muted);">Compare any two D-I teams on a Neutral, Home, or Away court.</p>
          </div>
          <button onclick="swapSimTeams()" class="px-2.5 py-1 text-xs font-semibold rounded-lg hi-subcard hover:opacity-80 cursor-pointer">
            ⇄ Swap Teams
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-xs font-semibold block mb-1.5" style="color: var(--hi-muted);">Team A</label>
            <select id="sim-a" onchange="runMatchupSim()" class="hi-input w-full text-sm rounded-xl p-2.5 font-medium cursor-pointer"></select>
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1.5" style="color: var(--hi-muted);">Team B</label>
            <select id="sim-b" onchange="runMatchupSim()" class="hi-input w-full text-sm rounded-xl p-2.5 font-medium cursor-pointer"></select>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <span class="text-xs font-medium mr-1" style="color: var(--hi-muted);">Venue:</span>
          <button onclick="setSimLoc('neutral')" id="loc-neutral" class="px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer">Neutral Court</button>
          <button onclick="setSimLoc('home_b')" id="loc-home_b" class="px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer">At Team B Home</button>
          <button onclick="setSimLoc('home_a')" id="loc-home_a" class="px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer">At Team A Home</button>
        </div>

        <div class="hi-subcard rounded-2xl p-5 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <div id="sim-name-a" class="text-xs font-bold" style="color: var(--hi-muted);">—</div>
              <div id="sim-pts-a" class="text-3xl font-extrabold tabular-nums mt-0.5">—</div>
            </div>
            <div class="text-center px-3">
              <div id="sim-line-badge" class="inline-block px-3 py-1 rounded-full text-xs font-extrabold" style="background-color: var(--hi-accent-soft); color: var(--hi-accent-text);">
                —
              </div>
              <div id="sim-total-sub" class="text-xs mt-1.5 tabular-nums" style="color: var(--hi-muted);">—</div>
            </div>
            <div class="text-right">
              <div id="sim-name-b" class="text-xs font-bold" style="color: var(--hi-muted);">—</div>
              <div id="sim-pts-b" class="text-3xl font-extrabold tabular-nums mt-0.5">—</div>
            </div>
          </div>

          <div class="w-full h-3 rounded-full overflow-hidden flex" style="background-color: var(--hi-border);">
            <div id="sim-bar-a" class="h-full transition-all duration-200" style="width: 50%; background-color: #ea580c;"></div>
            <div id="sim-bar-b" class="h-full transition-all duration-200" style="width: 50%; background-color: #3b82f6;"></div>
          </div>

          <div class="flex justify-between text-xs font-bold tabular-nums">
            <span id="sim-prob-a" style="color: #ea580c;">—</span>
            <span id="sim-prob-b" style="color: #3b82f6;">—</span>
          </div>

          <div id="sim-math-breakdown" class="pt-3 border-t flex flex-col sm:flex-row justify-between gap-2 text-xs" style="border-color: var(--hi-border); color: var(--hi-muted);"></div>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 4: METHODOLOGY BLURB ==================== -->
    <section id="tab-model" class="hidden max-w-3xl mx-auto">
      <div class="hi-card rounded-2xl p-6 md:p-8 space-y-5 text-sm leading-relaxed">
        <h2 class="text-lg font-extrabold">How HodgesIndex Works</h2>
        <p style="color: var(--hi-muted);">
          These ratings measure how many points per 100 possessions a college basketball team would outscore an average Division I opponent on a neutral court (<strong>Adjusted Efficiency Margin</strong>, or <code class="text-xs px-1.5 py-0.5 rounded hi-subcard font-mono">AdjEM</code>). Every morning, our model ingests every completed D-I box score and solves a simultaneous <strong>Weighted Ridge Regression</strong> across all 365 teams to separate true team quality from schedule strength and home-court advantage.
        </p>
        <ul class="space-y-3 list-disc pl-5" style="color: var(--hi-muted);">
          <li><strong style="color: var(--hi-text);">Tempo-Free & Possession-Weighted:</strong> Every game is converted into points per 100 possessions (<code class="text-xs font-mono">AdjO</code> for offense, <code class="text-xs font-mono">AdjD</code> for defense) and weighted by possessions. A separate Ridge solve computes opponent-adjusted pace (<code class="text-xs font-mono">AdjT</code>).</li>
          <li><strong style="color: var(--hi-text);">3-Point Luck Filtering:</strong> Using Empirical Bayes shrinkage toward the 34.0% D-I average, we regress 15% of single-game 3-point shooting variance back to each team's baseline so hot or cold shooting nights don't distort long-term ratings.</li>
          <li><strong style="color: var(--hi-text);">Garbage-Time Cap & Recency:</strong> Blowouts beyond 35 points per 100 possessions receive diminishing returns (25% slope), while a gentle daily decay (<code class="text-xs font-mono">0.9975/day</code>) gives slightly more weight to recent form.</li>
          <li><strong style="color: var(--hi-text);">Fading Preseason Priors:</strong> Early-season ratings are anchored toward a regressed prior from last season that automatically fades to <strong>zero</strong> once teams reach 14 games played in January—meaning conference play and March Madness are 100% earned on this season's court.</li>
          <li><strong style="color: var(--hi-text);">Altitude-Aware Home Court:</strong> Beyond standard home-court advantage (+4.0 pts/100 possessions), our model learns a dedicated elevation boost (+1.55 pts/100) for high-altitude Mountain West and Big 12 venues.</li>
        </ul>
        <p class="text-xs pt-3 border-t" style="border-color: var(--hi-border); color: var(--hi-muted);">
          Every hyperparameter was selected via chronological walk-forward backtesting across 5,500+ out-of-sample D-I games (70.7% straight-up winner accuracy, 9.03-point Jan–Apr spread MAE, and 0.5476 log-loss).
        </p>
      </div>
    </section>

  </div>

  <!-- Solid, Opaque Team Resume Modal -->
  <div id="team-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4" style="background-color: rgba(15, 23, 42, 0.65); backdrop-filter: blur(4px);" onclick="if(event.target===this) closeTeamModal()">
    <div class="hi-modal-card rounded-2xl max-w-xl w-full p-5 md:p-6 space-y-4 max-h-[85vh] flex flex-col">
      <div class="flex items-start justify-between border-b pb-3.5" style="border-color: var(--hi-border);">
        <div>
          <div class="flex items-center gap-2.5">
            <span id="modal-rk" class="text-xs font-extrabold px-2.5 py-1 rounded-lg" style="background-color: var(--hi-accent-soft); color: var(--hi-accent-text);">#1</span>
            <h3 id="modal-name" class="text-xl font-extrabold">—</h3>
          </div>
          <p id="modal-sub" class="text-xs mt-1" style="color: var(--hi-muted);">—</p>
        </div>
        <button onclick="closeTeamModal()" class="text-xs font-bold px-3 py-1.5 rounded-lg hi-subcard hover:opacity-80 cursor-pointer">✕ Close</button>
      </div>

      <div class="grid grid-cols-4 gap-2.5 text-center text-xs">
        <div class="p-3 rounded-xl hi-subcard">
          <div style="color: var(--hi-muted);">AdjEM</div>
          <div id="modal-em" class="font-mono font-extrabold text-sm mt-0.5">—</div>
        </div>
        <div class="p-3 rounded-xl hi-subcard">
          <div style="color: var(--hi-muted);">AdjO</div>
          <div id="modal-adjo" class="font-mono font-extrabold text-sm mt-0.5">—</div>
        </div>
        <div class="p-3 rounded-xl hi-subcard">
          <div style="color: var(--hi-muted);">AdjD</div>
          <div id="modal-adjd" class="font-mono font-extrabold text-sm mt-0.5">—</div>
        </div>
        <div class="p-3 rounded-xl hi-subcard">
          <div style="color: var(--hi-muted);">AdjT</div>
          <div id="modal-tempo" class="font-mono font-extrabold text-sm mt-0.5">—</div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-2 text-xs px-1" style="color: var(--hi-muted);">
        <span id="modal-ff" class="font-mono">—</span>
        <button onclick="sendModalTeamToSim()" class="font-bold hover:underline cursor-pointer" style="color: var(--hi-accent);">Simulate matchup →</button>
      </div>

      <div class="overflow-y-auto flex-1 border-t pt-2" style="border-color: var(--hi-border);">
        <table class="w-full text-left border-collapse text-xs">
          <thead style="color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
            <tr>
              <th class="py-2 px-2 font-bold">Date</th>
              <th class="py-2 px-2 font-bold">Loc</th>
              <th class="py-2 px-2 font-bold">Opponent</th>
              <th class="py-2 px-2 font-bold">Result</th>
              <th class="py-2 px-2 font-bold text-right">ORtg / DRtg</th>
            </tr>
          </thead>
          <tbody id="modal-logs-tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    const SITE_DATA = __SITE_PAYLOAD_PLACEHOLDER__;
    const TEAMS = SITE_DATA.teams;
    const SLATE = SITE_DATA.slate;
    const CFG = SITE_DATA.config;
    const TEAM_MAP = {};
    TEAMS.forEach(t => { TEAM_MAP[t.team] = t; });

    let modalTeamName = TEAMS[0].team;
    let activeSlateFilter = 'ALL';
    let simLoc = 'neutral';
    let usePrior = true;
    let activeTab = 'rankings';

    function toggleTheme() {
      const root = document.documentElement;
      const isDark = root.classList.contains('dark');
      if (isDark) {
        root.classList.remove('dark');
        root.classList.add('light');
        document.getElementById('theme-btn').textContent = '🌙 Dark';
      } else {
        root.classList.remove('light');
        root.classList.add('dark');
        document.getElementById('theme-btn').textContent = '☀️ Light';
      }
    }

    function tv(r) {
      if (usePrior) {
        return { rank: r.rank, adj_em: r.adj_em, adj_o: r.adj_o, adj_d: r.adj_d, o_rk: r.o_rk, d_rk: r.d_rk };
      }
      return { rank: r.np_rank, adj_em: r.np_adj_em, adj_o: r.np_adj_o, adj_d: r.np_adj_d, o_rk: r.np_o_rk, d_rk: r.np_d_rk };
    }

    function onTogglePrior() {
      usePrior = document.getElementById('toggle-prior').checked;
      document.getElementById('hdr-prior').textContent = usePrior ? SITE_DATA.prior_weight : '0 (2026–27 only)';
      updatePulseCards();
      renderRankingsTable();
      renderSlate();
      runMatchupSim();
    }

    function updatePulseCards() {
      const sortedByEM = [...TEAMS].sort((a, b) => tv(b).adj_em - tv(a).adj_em);
      const sortedByO = [...TEAMS].sort((a, b) => tv(b).adj_o - tv(a).adj_o);
      const sortedByD = [...TEAMS].sort((a, b) => tv(a).adj_d - tv(b).adj_d);
      const mover = SITE_DATA.kpis.mover1;

      const no1 = sortedByEM[0], v1 = tv(no1);
      const off1 = sortedByO[0], vo = tv(off1);
      const def1 = sortedByD[0], vd = tv(def1);

      document.getElementById('pulse-no1').textContent = `${no1.team} (${no1.record})`;
      document.getElementById('pulse-no1-sub').textContent = `+${v1.adj_em.toFixed(2)} AdjEM`;
      document.getElementById('pulse-off1').textContent = `${off1.team} (${off1.record})`;
      document.getElementById('pulse-off1-sub').textContent = `${vo.adj_o.toFixed(1)} pts / 100 poss`;
      document.getElementById('pulse-def1').textContent = `${def1.team} (${def1.record})`;
      document.getElementById('pulse-def1-sub').textContent = `${vd.adj_d.toFixed(1)} pts / 100 poss`;
      document.getElementById('pulse-mover').textContent = `${mover.team} (${mover.record})`;
      document.getElementById('pulse-mover-sub').textContent = `${mover.vs_prior >= 0 ? '+' : ''}${mover.vs_prior.toFixed(2)} vs prior`;
    }

    function openTopCard(which) {
      const sortedByEM = [...TEAMS].sort((a, b) => tv(b).adj_em - tv(a).adj_em);
      const sortedByO = [...TEAMS].sort((a, b) => tv(b).adj_o - tv(a).adj_o);
      const sortedByD = [...TEAMS].sort((a, b) => tv(a).adj_d - tv(b).adj_d);
      if (which === 'no1') openTeamModal(sortedByEM[0].team);
      else if (which === 'off1') openTeamModal(sortedByO[0].team);
      else if (which === 'def1') openTeamModal(sortedByD[0].team);
      else openTeamModal(SITE_DATA.kpis.mover1.team);
    }

    function switchMainTab(tab) {
      activeTab = tab;
      ['rankings', 'slate', 'matchup', 'model'].forEach(t => {
        const btn = document.getElementById('nav-' + t);
        const pane = document.getElementById('tab-' + t);
        if (t === tab) {
          btn.style.backgroundColor = 'var(--hi-accent)';
          btn.style.color = '#ffffff';
          pane.classList.remove('hidden');
        } else {
          btn.style.backgroundColor = 'transparent';
          btn.style.color = 'var(--hi-muted)';
          pane.classList.add('hidden');
        }
      });
    }

    function renderRankingsTable() {
      const q = document.getElementById('rank-search').value.trim().toLowerCase();
      const conf = document.getElementById('rank-conf').value;
      const sortKey = document.getElementById('rank-sort').value;

      let rows = TEAMS.filter(r => {
        if (conf !== 'ALL' && r.conf !== conf) return false;
        if (q && !r.team.toLowerCase().includes(q)) return false;
        return true;
      });

      if (sortKey === 'tempo') {
        rows.sort((a, b) => b.tempo - a.tempo);
      } else if (sortKey === 'adj_d') {
        rows.sort((a, b) => tv(a).adj_d - tv(b).adj_d);
      } else {
        rows.sort((a, b) => tv(b)[sortKey] - tv(a)[sortKey]);
      }

      document.getElementById('rank-count-label').textContent = `${rows.length} teams`;

      const tbody = document.getElementById('rankings-tbody');
      tbody.innerHTML = rows.map(r => {
        const v = tv(r);
        let rkBadgeStyle = 'color: var(--hi-muted);';
        if (v.rank <= 10) {
          rkBadgeStyle = 'background-color: var(--hi-accent-soft); color: var(--hi-accent-text); font-weight: 800; padding: 2px 7px; border-radius: 6px;';
        } else if (v.rank <= 25) {
          rkBadgeStyle = 'background-color: var(--hi-surface-alt); color: var(--hi-text); font-weight: 700; padding: 2px 7px; border-radius: 6px;';
        }

        const oBadge = v.o_rk <= 15 ? 'color: var(--hi-pos); font-weight: 700;' : 'color: var(--hi-muted);';
        const dBadge = v.d_rk <= 15 ? 'color: var(--hi-pos); font-weight: 700;' : 'color: var(--hi-muted);';

        return `
        <tr class="hi-row cursor-pointer" onclick="openTeamModal('${r.team.replace(/'/g, "\\'")}')">
          <td class="py-2.5 px-4 tabular-nums"><span style="${rkBadgeStyle}">${v.rank}</span></td>
          <td class="py-2.5 px-4 font-bold">
            ${r.team}${r.alt ? '<span title="High-Altitude Venue (+1.55 HCA)" class="ml-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-600">⛰️ ALT</span>' : ''}
          </td>
          <td class="py-2.5 px-3 text-xs font-semibold" style="color: var(--hi-muted);">${r.conf}</td>
          <td class="py-2.5 px-3 text-xs tabular-nums" style="color: var(--hi-muted);">${r.record}</td>
          <td class="py-2.5 px-4 text-right font-mono font-extrabold tabular-nums" style="color: ${v.adj_em >= 0 ? 'var(--hi-pos)' : 'var(--hi-neg)'};">
            ${v.adj_em >= 0 ? '+' : ''}${v.adj_em.toFixed(2)}
          </td>
          <td class="py-2.5 px-4 text-right font-mono tabular-nums">
            ${v.adj_o.toFixed(1)} <span class="text-xs ml-0.5" style="${oBadge}">#${v.o_rk}</span>
          </td>
          <td class="py-2.5 px-4 text-right font-mono tabular-nums">
            ${v.adj_d.toFixed(1)} <span class="text-xs ml-0.5" style="${dBadge}">#${v.d_rk}</span>
          </td>
          <td class="py-2.5 px-4 text-right font-mono tabular-nums" style="color: var(--hi-muted);">${r.tempo.toFixed(1)}</td>
        </tr>
      `;}).join('');
    }

    function openTeamModal(teamName) {
      modalTeamName = teamName;
      const r = TEAM_MAP[teamName];
      if (!r) return;
      const v = tv(r);

      document.getElementById('modal-rk').textContent = `#${v.rank}`;
      document.getElementById('modal-name').textContent = r.team;
      document.getElementById('modal-sub').textContent = `${r.conf} Conference · ${r.record} Record · Live T-Rank #${r.torvik_rk}`;
      document.getElementById('modal-em').textContent = `${v.adj_em >= 0 ? '+' : ''}${v.adj_em.toFixed(2)}`;
      document.getElementById('modal-em').style.color = v.adj_em >= 0 ? 'var(--hi-pos)' : 'var(--hi-neg)';
      document.getElementById('modal-adjo').textContent = `${v.adj_o.toFixed(1)} (#${v.o_rk})`;
      document.getElementById('modal-adjd').textContent = `${v.adj_d.toFixed(1)} (#${v.d_rk})`;
      document.getElementById('modal-tempo').textContent = r.tempo.toFixed(1);
      document.getElementById('modal-ff').textContent = `eFG ${r.efg}% · ORB ${r.orb}% · Opp ORB ${r.opp_orb}% · TOV ${r.tov}%`;

      const logTbody = document.getElementById('modal-logs-tbody');
      if (!r.logs || r.logs.length === 0) {
        logTbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center" style="color: var(--hi-muted);">No completed D-I games yet.</td></tr>`;
      } else {
        logTbody.innerHTML = r.logs.map(lg => `
          <tr class="hi-row">
            <td class="py-2 px-2 tabular-nums" style="color: var(--hi-muted);">${lg.date}</td>
            <td class="py-2 px-2">${lg.loc}</td>
            <td class="py-2 px-2 font-bold cursor-pointer hover:underline" onclick="openTeamModal('${lg.opp.replace(/'/g, "\\'")}')">
              #${lg.opp_rk} ${lg.opp}
            </td>
            <td class="py-2 px-2 font-extrabold tabular-nums" style="color: ${lg.win ? 'var(--hi-pos)' : 'var(--hi-neg)'};">
              ${lg.win ? 'W' : 'L'} ${lg.score}
            </td>
            <td class="py-2 px-2 text-right font-mono tabular-nums" style="color: var(--hi-muted);">${lg.ortg} / ${lg.drtg}</td>
          </tr>
        `).join('');
      }
      document.getElementById('team-modal').classList.remove('hidden');
    }

    function closeTeamModal() {
      document.getElementById('team-modal').classList.add('hidden');
    }

    function sendModalTeamToSim() {
      closeTeamModal();
      document.getElementById('sim-a').value = modalTeamName;
      switchMainTab('matchup');
      runMatchupSim();
    }

    function renderSlateFilterButtons() {
      const container = document.getElementById('slate-filter-btns');
      const btns = [{ key: 'ALL', label: 'All Dates' }, ...SITE_DATA.slate_dates];
      container.innerHTML = btns.map(b => {
        const isActive = b.key === activeSlateFilter;
        const style = isActive
          ? 'background-color: var(--hi-accent); color: #ffffff;'
          : 'background-color: var(--hi-surface-alt); color: var(--hi-muted); border: 1px solid var(--hi-border);';
        return `<button onclick="setSlateFilter('${b.key}')" style="${style}" class="px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer">${b.label}</button>`;
      }).join('');
    }

    function setSlateFilter(filterVal) {
      activeSlateFilter = filterVal;
      renderSlateFilterButtons();
      renderSlate();
    }

    function renderSlate() {
      const featuredOnly = document.getElementById('slate-featured-only').checked;
      const games = SLATE.filter(g => {
        if (activeSlateFilter !== 'ALL' && g.date !== activeSlateFilter) return false;
        const r1 = usePrior ? g.r1 : TEAM_MAP[g.t1].np_rank;
        const r2 = usePrior ? g.r2 : TEAM_MAP[g.t2].np_rank;
        if (featuredOnly && r1 > 60 && r2 > 60) return false;
        return true;
      });

      const tbody = document.getElementById('slate-tbody');
      if (games.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-xs" style="color: var(--hi-muted);">No games match this filter. Uncheck "Featured matchups only" to see all D-I games.</td></tr>`;
        return;
      }

      const mu = usePrior ? SITE_DATA.mu : SITE_DATA.mu_np;
      tbody.innerHTML = games.map(g => {
        const statusCell = g.is_final
          ? `<span class="text-xs font-extrabold px-2 py-0.5 rounded" style="background-color: rgba(16, 185, 129, 0.15); color: var(--hi-pos);">FINAL: ${g.actual}</span>`
          : `<span class="text-xs" style="color: var(--hi-muted);">${g.neutral ? 'Neutral Site' : 'Home / Away'}</span>`;

        let p1 = g.pred1, p2 = g.pred2, fav = g.fav, spr = g.spread, favProb = Math.max(g.prob1, g.prob2);
        let rk1 = g.r1, rk2 = g.r2;
        if (!usePrior) {
          const a = TEAM_MAP[g.t1], b = TEAM_MAP[g.t2];
          rk1 = a.np_rank; rk2 = b.np_rank;
          const poss = 0.5 * (a.tempo + b.tempo);
          const hca = g.neutral ? 0.0 : (CFG.std_hca + (b.alt ? CFG.alt_hca : 0.0));
          p1 = (a.np_adj_o + b.np_adj_d - mu - 0.5 * hca) * (poss / 100.0);
          p2 = (b.np_adj_o + a.np_adj_d - mu + 0.5 * hca) * (poss / 100.0);
          const diff2 = p2 - p1;
          fav = diff2 >= 0 ? g.t2 : g.t1;
          spr = Math.abs(diff2);
          const prob2 = 100.0 / (1.0 + Math.exp(-1.702 * (diff2 / CFG.prob_sigma)));
          favProb = Math.max(prob2, 100.0 - prob2);
        }

        return `
          <tr onclick="openMatchupFromSlate('${g.t1.replace(/'/g, "\\'")}', '${g.t2.replace(/'/g, "\\'")}', ${g.neutral})" class="hi-row cursor-pointer">
            <td class="py-3 px-4 text-xs font-medium whitespace-nowrap" style="color: var(--hi-muted);">${g.date_label}</td>
            <td class="py-3 px-4">
              <span class="font-bold">#${rk1} ${g.t1}</span>
              <span class="text-xs mx-1.5" style="color: var(--hi-muted);">${g.neutral ? 'vs.' : 'at'}</span>
              <span class="font-bold">#${rk2} ${g.t2}</span>
            </td>
            <td class="py-3 px-4 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${p1.toFixed(0)}–${p2.toFixed(0)}</td>
            <td class="py-3 px-4 text-right font-mono text-xs font-extrabold tabular-nums" style="color: var(--hi-accent);">${fav} -${spr.toFixed(1)}</td>
            <td class="py-3 px-4 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${favProb.toFixed(0)}%</td>
            <td class="py-3 px-4 text-right">${statusCell}</td>
          </tr>
        `;
      }).join('');
    }

    function openMatchupFromSlate(t1, t2, isNeutral) {
      document.getElementById('sim-a').value = t1;
      document.getElementById('sim-b').value = t2;
      setSimLoc(isNeutral ? 'neutral' : 'home_b');
      switchMainTab('matchup');
    }

    function swapSimTeams() {
      const selA = document.getElementById('sim-a');
      const selB = document.getElementById('sim-b');
      const tmp = selA.value;
      selA.value = selB.value;
      selB.value = tmp;
      runMatchupSim();
    }

    function setSimLoc(loc) {
      simLoc = loc;
      ['neutral', 'home_b', 'home_a'].forEach(l => {
        const btn = document.getElementById('loc-' + l);
        if (l === loc) {
          btn.style.backgroundColor = 'var(--hi-accent)';
          btn.style.color = '#ffffff';
        } else {
          btn.style.backgroundColor = 'var(--hi-surface-alt)';
          btn.style.color = 'var(--hi-muted)';
        }
      });
      runMatchupSim();
    }

    function runMatchupSim() {
      const a = TEAM_MAP[document.getElementById('sim-a').value];
      const b = TEAM_MAP[document.getElementById('sim-b').value];
      if (!a || !b) return;
      const va = tv(a), vb = tv(b);

      const mu = usePrior ? SITE_DATA.mu : SITE_DATA.mu_np;
      const estPoss = 0.5 * (a.tempo + b.tempo);

      let hcaA = 0.0;
      if (simLoc === 'home_a') hcaA = CFG.std_hca + (a.alt ? CFG.alt_hca : 0.0);
      else if (simLoc === 'home_b') hcaA = -(CFG.std_hca + (b.alt ? CFG.alt_hca : 0.0));

      const ptsA = (va.adj_o + vb.adj_d - mu + 0.5 * hcaA) * (estPoss / 100.0);
      const ptsB = (vb.adj_o + va.adj_d - mu - 0.5 * hcaA) * (estPoss / 100.0);
      const diffA = ptsA - ptsB;

      const probA = 100.0 / (1.0 + Math.exp(-1.702 * (diffA / CFG.prob_sigma)));
      const probB = 100.0 - probA;

      document.getElementById('sim-name-a').textContent = `#${va.rank} ${a.team} (${a.record})`;
      document.getElementById('sim-name-b').textContent = `#${vb.rank} ${b.team} (${b.record})`;
      document.getElementById('sim-pts-a').textContent = ptsA.toFixed(1);
      document.getElementById('sim-pts-b').textContent = ptsB.toFixed(1);

      const fav = diffA >= 0 ? a.team : b.team;
      document.getElementById('sim-line-badge').textContent = `${fav} -${Math.abs(diffA).toFixed(1)}`;
      document.getElementById('sim-total-sub').textContent = `Projected Total ${(ptsA + ptsB).toFixed(1)} · ${estPoss.toFixed(1)} poss`;

      document.getElementById('sim-bar-a').style.width = `${probA.toFixed(1)}%`;
      document.getElementById('sim-bar-b').style.width = `${probB.toFixed(1)}%`;
      document.getElementById('sim-prob-a').textContent = `${a.team} ${probA.toFixed(1)}%`;
      document.getElementById('sim-prob-b').textContent = `${b.team} ${probB.toFixed(1)}%`;

      const baseDiff = (va.adj_em - vb.adj_em) * (estPoss / 100.0);
      const hcaPts = hcaA * (estPoss / 100.0);
      document.getElementById('sim-math-breakdown').innerHTML = `
        <span>Neutral edge: <strong style="color: var(--hi-text);">${baseDiff >= 0 ? a.team : b.team} +${Math.abs(baseDiff).toFixed(1)} pts</strong></span>
        <span>Court/Altitude: <strong style="color: var(--hi-text);">${Math.abs(hcaPts) < 0.05 ? 'Neutral (0.0)' : (hcaPts > 0 ? a.team + ' +' + hcaPts.toFixed(1) : b.team + ' +' + Math.abs(hcaPts).toFixed(1)) + ' pts'}</strong></span>
        <span>Offensive Glass: <strong style="color: var(--hi-text);">${a.orb}% vs ${b.orb}%</strong></span>
      `;
    }

    window.addEventListener('DOMContentLoaded', () => {
      document.getElementById('hdr-date').textContent = SITE_DATA.updated_at;
      document.getElementById('hdr-games').textContent = SITE_DATA.games_count.toLocaleString();
      document.getElementById('hdr-prior').textContent = SITE_DATA.prior_weight;

      const confs = Array.from(new Set(TEAMS.map(t => t.conf))).sort();
      const confSel = document.getElementById('rank-conf');
      confs.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        confSel.appendChild(opt);
      });

      const simA = document.getElementById('sim-a');
      const simB = document.getElementById('sim-b');
      TEAMS.forEach(r => {
        const o1 = document.createElement('option');
        o1.value = r.team;
        o1.textContent = `#${r.rank} ${r.team} (${r.conf})`;
        simA.appendChild(o1);

        const o2 = document.createElement('option');
        o2.value = r.team;
        o2.textContent = `#${r.rank} ${r.team} (${r.conf})`;
        simB.appendChild(o2);
      });
      simA.value = TEAMS[0].team;
      simB.value = TEAMS[1].team;

      switchMainTab('rankings');
      setSimLoc('neutral');
      updatePulseCards();
      renderRankingsTable();
      renderSlateFilterButtons();
      renderSlate();
      runMatchupSim();
    });
  </script>
</body>
</html>
"""

final_html = HTML_TEMPLATE.replace("__SITE_PAYLOAD_PLACEHOLDER__", PAYLOAD_JSON)
(DATA_DIR / "index.html").write_text(final_html)
(DATA_DIR / "generated_site.html").write_text(final_html)
if ARTIFACT_DIR.exists():
    (ARTIFACT_DIR / "hodges_basketball_ratings.html").write_text(final_html)
    (ARTIFACT_DIR / "cbb_ranking_laboratory.html").write_text(final_html)
print("Rendered standalone HodgesIndex UI (index.html):", len(final_html), "bytes")
