#!/usr/bin/env python3
"""
Renders HodgesIndex (index.html, generated_site.html, and artifact copies)
with a clean, authentic sports-analytics design:
- Solid standalone Light & Dark themes (opaque modals & sticky headers on GitHub Pages)
- Zero emojis, zero AI-template cards, crisp editorial typography & tabular numbers
- Historical Rankings & Daily Pick Performance Tracker tab
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
  <title>HodgesIndex · 2026–27 College Basketball Ratings</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    html.light {
      --hi-bg: #f8fafc;
      --hi-surface: #ffffff;
      --hi-surface-alt: #f1f5f9;
      --hi-surface-hover: #f8fafc;
      --hi-border: #e2e8f0;
      --hi-text: #0f172a;
      --hi-muted: #64748b;
      --hi-accent: #c2410c;
      --hi-accent-soft: #ffedd5;
      --hi-accent-text: #9a3412;
      --hi-pos: #047857;
      --hi-neg: #be123c;
      --hi-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
      --hi-modal-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.35);
    }
    html.dark {
      --hi-bg: #0b0f19;
      --hi-surface: #111827;
      --hi-surface-alt: #1e293b;
      --hi-surface-hover: #1a2333;
      --hi-border: #1f2937;
      --hi-text: #f8fafc;
      --hi-muted: #94a3b8;
      --hi-accent: #f97316;
      --hi-accent-soft: rgba(249, 115, 22, 0.15);
      --hi-accent-text: #fdba74;
      --hi-pos: #10b981;
      --hi-neg: #f43f5e;
      --hi-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
      --hi-modal-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.75);
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
      transition: background-color 0.1s ease;
    }
    .hi-row:hover {
      background-color: var(--hi-surface-alt);
    }
    .tabular-nums { font-variant-numeric: tabular-nums; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--hi-border); border-radius: 3px; }
  </style>
</head>
<body class="antialiased min-h-screen p-4 md:p-8">

  <div class="max-w-5xl mx-auto space-y-5">

    <!-- Clean Editorial Masthead -->
    <header class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-4" style="border-bottom: 2px solid var(--hi-text);">
      <div>
        <div class="flex items-baseline gap-3">
          <h1 class="text-2xl font-bold tracking-tight">HodgesIndex</h1>
          <span class="text-xs font-medium" style="color: var(--hi-muted);">2026–27 D-I College Basketball</span>
        </div>
        <p class="text-xs mt-1" style="color: var(--hi-muted);">
          Updated <span id="hdr-date" class="font-medium" style="color: var(--hi-text);">—</span> ·
          <span id="hdr-games">—</span> games ·
          SU <span id="hdr-record" class="font-mono font-medium tabular-nums" style="color: var(--hi-text);">—</span> ·
          ATS <span id="hdr-ats" class="font-mono font-medium tabular-nums" style="color: var(--hi-text);">—</span> ·
          Prior weight <span id="hdr-prior" class="font-mono tabular-nums" style="color: var(--hi-text);">—</span>
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-5 text-sm">
        <nav class="flex flex-wrap items-center gap-5">
          <button onclick="switchMainTab('rankings')" id="nav-rankings" class="pb-1 font-semibold transition cursor-pointer">
            Rankings
          </button>
          <button onclick="switchMainTab('slate')" id="nav-slate" class="pb-1 font-medium transition cursor-pointer">
            Games
          </button>
          <button onclick="switchMainTab('history')" id="nav-history" class="pb-1 font-medium transition cursor-pointer">
            Performance
          </button>
          <button onclick="switchMainTab('matchup')" id="nav-matchup" class="pb-1 font-medium transition cursor-pointer">
            Predictor
          </button>
          <button onclick="switchMainTab('model')" id="nav-model" class="pb-1 font-medium transition cursor-pointer">
            Methodology
          </button>
        </nav>

        <button onclick="toggleTheme()" id="theme-btn"
          class="px-2.5 py-1 text-xs font-medium rounded border transition cursor-pointer"
          style="border-color: var(--hi-border); color: var(--hi-muted); background-color: var(--hi-surface);">
          Dark
        </button>
      </div>
    </header>

    <!-- ==================== TAB 1: RANKINGS TABLE ==================== -->
    <section id="tab-rankings" class="space-y-3">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2">
          <input id="rank-search" type="text" placeholder="Filter team..." oninput="renderRankingsTable()"
            class="hi-input px-3 py-1.5 text-xs rounded-md w-48" />
          <select id="rank-conf" onchange="renderRankingsTable()" class="hi-input px-2.5 py-1.5 text-xs rounded-md cursor-pointer">
            <option value="ALL">All Conferences</option>
          </select>
          <select id="rank-sort" onchange="renderRankingsTable()" class="hi-input px-2.5 py-1.5 text-xs rounded-md cursor-pointer">
            <option value="adj_em">Sort: Overall (AdjEM)</option>
            <option value="adj_o">Sort: Offense (AdjO)</option>
            <option value="adj_d">Sort: Defense (AdjD)</option>
            <option value="tempo">Sort: Tempo (AdjT)</option>
          </select>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <label class="inline-flex items-center gap-1.5 text-xs cursor-pointer select-none" style="color: var(--hi-muted);">
            <input id="toggle-prior" type="checkbox" checked onchange="onTogglePrior()" class="rounded cursor-pointer" style="accent-color: var(--hi-accent);" />
            <span>Include prior-season weighting</span>
          </label>
          <span id="rank-count-label" class="text-xs tabular-nums" style="color: var(--hi-muted);">365 teams</span>
        </div>
      </div>

      <div class="hi-card rounded-lg overflow-hidden">
        <div class="overflow-x-auto max-h-[660px] overflow-y-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 text-xs" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
              <tr>
                <th class="py-2.5 px-3.5 font-semibold w-12">Rk</th>
                <th class="py-2.5 px-3.5 font-semibold">Team</th>
                <th class="py-2.5 px-3 font-semibold">Conf</th>
                <th class="py-2.5 px-3 font-semibold">W–L</th>
                <th class="py-2.5 px-3.5 font-semibold text-right" title="Adjusted Efficiency Margin">AdjEM</th>
                <th class="py-2.5 px-3.5 font-semibold text-right" title="Adjusted Offensive Efficiency">AdjO</th>
                <th class="py-2.5 px-3.5 font-semibold text-right" title="Adjusted Defensive Efficiency">AdjD</th>
                <th class="py-2.5 px-3.5 font-semibold text-right" title="Adjusted Tempo">AdjT</th>
              </tr>
            </thead>
            <tbody id="rankings-tbody" class="text-sm"></tbody>
          </table>
        </div>
        <div class="px-3.5 py-2 text-xs flex flex-wrap items-center justify-between gap-2" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-top: 1px solid var(--hi-border);">
          <span><strong>ALT</strong> = High-altitude home venue (+1.55 pts/100 poss elevation adjustment)</span>
          <span>Click any team for game log</span>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 2: GAMES SLATE ==================== -->
    <section id="tab-slate" class="hidden space-y-3">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div id="slate-filter-btns" class="flex flex-wrap items-center gap-1.5"></div>
        <label class="inline-flex items-center gap-1.5 text-xs cursor-pointer" style="color: var(--hi-muted);">
          <input id="slate-featured-only" type="checkbox" checked onchange="renderSlate()" class="rounded cursor-pointer" style="accent-color: var(--hi-accent);" />
          <span>Featured games only (Top 60)</span>
        </label>
      </div>

      <div class="hi-card rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="text-xs" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
              <tr>
                <th class="py-2.5 px-4 font-semibold">Date</th>
                <th class="py-2.5 px-4 font-semibold">Matchup</th>
                <th class="py-2.5 px-4 font-semibold text-right">Projection</th>
                <th class="py-2.5 px-4 font-semibold text-right">Model Line</th>
                <th class="py-2.5 px-4 font-semibold text-right">Vegas Line</th>
                <th class="py-2.5 px-4 font-semibold text-right">Win Prob</th>
                <th class="py-2.5 px-4 font-semibold text-right">Status</th>
              </tr>
            </thead>
            <tbody id="slate-tbody" class="text-sm"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 3: HISTORICAL PERFORMANCE & ARCHIVE ==================== -->
    <section id="tab-history" class="hidden space-y-4">
      <!-- Season Summary & Calibration Strip -->
      <div class="hi-card rounded-lg p-4 space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b" style="border-color: var(--hi-border);">
          <div>
            <h2 class="text-sm font-bold">2026–27 Walk-Forward Model Performance</h2>
            <p class="text-xs" style="color: var(--hi-muted);">Strictly out-of-sample pre-game picks evaluated Straight-Up (SU) and Against the Vegas Spread (ATS).</p>
          </div>
          <div class="flex flex-wrap items-center gap-4 text-xs font-mono tabular-nums">
            <span>Straight-Up: <strong id="hist-season-rec" style="color: var(--hi-pos);">—</strong></span>
            <span>Vegas ATS: <strong id="hist-season-ats" style="color: var(--hi-text);">—</strong></span>
            <span>Spread MAE: <strong id="hist-season-mae" style="color: var(--hi-text);">—</strong></span>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs" id="hist-buckets-grid"></div>
      </div>

      <!-- Date Selector & Sub-View Controls -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2">
          <label class="text-xs font-medium" style="color: var(--hi-muted);">Date:</label>
          <select id="hist-date-select" onchange="onSelectHistoryDate()" class="hi-input px-3 py-1.5 text-xs font-medium rounded-md cursor-pointer"></select>
          <span id="hist-day-summary" class="text-xs font-mono tabular-nums ml-1" style="color: var(--hi-muted);"></span>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <div class="flex flex-wrap items-center gap-1" id="hist-filter-group">
            <button onclick="setHistOutcomeFilter('ALL')" id="hfilt-ALL" class="px-2.5 py-1 text-xs font-medium rounded transition cursor-pointer">All</button>
            <button onclick="setHistOutcomeFilter('ATS_W')" id="hfilt-ATS_W" class="px-2.5 py-1 text-xs font-medium rounded transition cursor-pointer">ATS Wins</button>
            <button onclick="setHistOutcomeFilter('ATS_L')" id="hfilt-ATS_L" class="px-2.5 py-1 text-xs font-medium rounded transition cursor-pointer">ATS Losses</button>
            <button onclick="setHistOutcomeFilter('MISS')" id="hfilt-MISS" class="px-2.5 py-1 text-xs font-medium rounded transition cursor-pointer">SU Upsets</button>
          </div>
          <span style="color: var(--hi-border);">|</span>
          <button onclick="toggleHistMode()" id="hist-mode-btn" class="px-2.5 py-1 text-xs font-medium rounded hi-subcard hover:opacity-80 cursor-pointer">
            View Pre-Game Top 40 Rankings
          </button>
        </div>
      </div>

      <!-- Daily Picks Table -->
      <div id="hist-picks-card" class="hi-card rounded-lg overflow-hidden">
        <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 text-xs" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
              <tr>
                <th class="py-2.5 px-3 font-semibold w-14">SU</th>
                <th class="py-2.5 px-3 font-semibold">Matchup (Pre-Game Rk)</th>
                <th class="py-2.5 px-3 font-semibold text-right">Model Line</th>
                <th class="py-2.5 px-3 font-semibold text-right">Vegas Line</th>
                <th class="py-2.5 px-3 font-semibold text-right">ATS Pick</th>
                <th class="py-2.5 px-3 font-semibold text-right">Actual Score</th>
                <th class="py-2.5 px-3 font-semibold text-right">Err</th>
              </tr>
            </thead>
            <tbody id="hist-picks-tbody" class="text-sm"></tbody>
          </table>
        </div>
      </div>

      <!-- Historical Top 40 Rankings Snapshot Table -->
      <div id="hist-ranks-card" class="hidden hi-card rounded-lg overflow-hidden">
        <div class="px-4 py-2.5 text-xs border-b flex items-center justify-between" style="background-color: var(--hi-surface-alt); border-color: var(--hi-border); color: var(--hi-muted);">
          <span id="hist-ranks-title" class="font-semibold" style="color: var(--hi-text);">Pre-Game Top 40 Rankings Snapshot</span>
          <span>Full 365-team daily files archived in <code class="font-mono">history/YYYY-MM-DD.json</code></span>
        </div>
        <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 text-xs" style="background-color: var(--hi-surface-alt); color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
              <tr>
                <th class="py-2 px-3.5 font-semibold w-12">Rk</th>
                <th class="py-2 px-3.5 font-semibold">Team</th>
                <th class="py-2 px-3 font-semibold">Conf</th>
                <th class="py-2 px-3 font-semibold">Entering W–L</th>
                <th class="py-2 px-3.5 font-semibold text-right">AdjEM</th>
                <th class="py-2 px-3.5 font-semibold text-right">AdjO</th>
                <th class="py-2 px-3.5 font-semibold text-right">AdjD</th>
                <th class="py-2 px-3.5 font-semibold text-right">AdjT</th>
              </tr>
            </thead>
            <tbody id="hist-ranks-tbody" class="text-sm"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 4: HEAD-TO-HEAD PREDICTOR ==================== -->
    <section id="tab-matchup" class="hidden max-w-2xl mx-auto pt-2">
      <div class="hi-card rounded-lg p-6 space-y-5">
        <div class="flex items-center justify-between border-b pb-3" style="border-color: var(--hi-border);">
          <div>
            <h2 class="text-base font-bold">Matchup Predictor</h2>
            <p class="text-xs mt-0.5" style="color: var(--hi-muted);">Neutral, Home, or Away projection using current HodgesIndex ratings.</p>
          </div>
          <button onclick="swapSimTeams()" class="px-2.5 py-1 text-xs font-medium rounded hi-subcard hover:opacity-80 cursor-pointer">
            Swap Teams
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-xs font-medium block mb-1" style="color: var(--hi-muted);">Team A</label>
            <select id="sim-a" onchange="runMatchupSim()" class="hi-input w-full text-sm rounded-md p-2 cursor-pointer"></select>
          </div>
          <div>
            <label class="text-xs font-medium block mb-1" style="color: var(--hi-muted);">Team B</label>
            <select id="sim-b" onchange="runMatchupSim()" class="hi-input w-full text-sm rounded-md p-2 cursor-pointer"></select>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="setSimLoc('neutral')" id="loc-neutral" class="px-3 py-1.5 text-xs font-medium rounded-md transition cursor-pointer">Neutral</button>
          <button onclick="setSimLoc('home_b')" id="loc-home_b" class="px-3 py-1.5 text-xs font-medium rounded-md transition cursor-pointer">At Team B</button>
          <button onclick="setSimLoc('home_a')" id="loc-home_a" class="px-3 py-1.5 text-xs font-medium rounded-md transition cursor-pointer">At Team A</button>
        </div>

        <div class="hi-subcard rounded-lg p-5 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <div id="sim-name-a" class="text-xs font-medium" style="color: var(--hi-muted);">—</div>
              <div id="sim-pts-a" class="text-3xl font-bold tabular-nums mt-0.5">—</div>
            </div>
            <div class="text-center px-3">
              <div id="sim-line-badge" class="text-sm font-bold">—</div>
              <div id="sim-total-sub" class="text-xs mt-0.5 tabular-nums" style="color: var(--hi-muted);">—</div>
            </div>
            <div class="text-right">
              <div id="sim-name-b" class="text-xs font-medium" style="color: var(--hi-muted);">—</div>
              <div id="sim-pts-b" class="text-3xl font-bold tabular-nums mt-0.5">—</div>
            </div>
          </div>

          <div class="w-full h-2 rounded-full overflow-hidden flex" style="background-color: var(--hi-border);">
            <div id="sim-bar-a" class="h-full transition-all duration-200" style="width: 50%; background-color: var(--hi-accent);"></div>
            <div id="sim-bar-b" class="h-full transition-all duration-200" style="width: 50%; background-color: #475569;"></div>
          </div>

          <div class="flex justify-between text-xs font-medium tabular-nums" style="color: var(--hi-muted);">
            <span id="sim-prob-a">—</span>
            <span id="sim-prob-b">—</span>
          </div>

          <div id="sim-math-breakdown" class="pt-3 border-t flex flex-col sm:flex-row justify-between gap-2 text-xs" style="border-color: var(--hi-border); color: var(--hi-muted);"></div>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 5: METHODOLOGY ==================== -->
    <section id="tab-model" class="hidden max-w-3xl mx-auto">
      <div class="hi-card rounded-lg p-6 md:p-8 space-y-4 text-sm leading-relaxed">
        <h2 class="text-base font-bold">Methodology</h2>
        <p style="color: var(--hi-muted);">
          HodgesIndex measures how many points per 100 possessions a Division I team would outscore an average opponent on a neutral court (<strong>Adjusted Efficiency Margin</strong>, or <code class="text-xs px-1 py-0.5 rounded hi-subcard font-mono">AdjEM</code>). Every morning, the model ingests all completed D-I box scores and solves a simultaneous <strong>Weighted Ridge Regression</strong> across all 365 teams.
        </p>
        <ul class="space-y-2.5 list-disc pl-5" style="color: var(--hi-muted);">
          <li><strong style="color: var(--hi-text);">Tempo-Free & Possession-Weighted:</strong> Games are evaluated per 100 possessions (<code class="text-xs font-mono">AdjO</code> and <code class="text-xs font-mono">AdjD</code>) and weighted by possessions. A separate Ridge solve computes opponent-adjusted pace (<code class="text-xs font-mono">AdjT</code>).</li>
          <li><strong style="color: var(--hi-text);">3-Point Luck Filtering:</strong> Using Empirical Bayes shrinkage toward the 34.0% D-I mean, 15% of single-game 3-point shooting variance is regressed back to each team's baseline before solving the ratings.</li>
          <li><strong style="color: var(--hi-text);">Expectation-Anchored Garbage-Time Cap & Recency:</strong> In competitive matchups, single-game margins beyond 26 points per 100 possessions (~18 actual points) receive diminishing returns (25% slope). In heavy buy-game mismatches where the expected spread already exceeds 18 points, the cap anchors at the expected margin so favorites aren't penalized for winning by their expected spread while still discounting garbage-time run-ups beyond expectation by 75%. Games are weighted by recency (<code class="text-xs font-mono">0.9975/day</code>).</li>
          <li><strong style="color: var(--hi-text);">Fading Preseason Priors:</strong> Early-season ratings blend a 0.95x prior from last season that decays linearly to zero by Game 14 in January. You can uncheck <em>Include prior-season weighting</em> at any time to view pure in-season ratings.</li>
          <li><strong style="color: var(--hi-text);">Altitude Home Court:</strong> In addition to standard home-court advantage (+4.0 pts/100 possessions), high-elevation venues receive a learned +1.55 pts/100 adjustment.</li>
          <li><strong style="color: var(--hi-text);">Historical Snapshots & Walk-Forward Audit:</strong> Every completed game day's pre-game rankings and picks are archived in <code class="text-xs font-mono">history/YYYY-MM-DD.json</code> and audited in the Performance tab.</li>
        </ul>
      </div>
    </section>

  </div>

  <!-- Solid Opaque Team Resume Modal -->
  <div id="team-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4" style="background-color: rgba(15, 23, 42, 0.6);" onclick="if(event.target===this) closeTeamModal()">
    <div class="hi-modal-card rounded-lg max-w-xl w-full p-5 space-y-4 max-h-[85vh] flex flex-col">
      <div class="flex items-start justify-between border-b pb-3" style="border-color: var(--hi-border);">
        <div>
          <div class="flex items-baseline gap-2">
            <span id="modal-rk" class="text-sm font-mono font-bold" style="color: var(--hi-muted);">#1</span>
            <h3 id="modal-name" class="text-lg font-bold">—</h3>
          </div>
          <p id="modal-sub" class="text-xs mt-0.5" style="color: var(--hi-muted);">—</p>
        </div>
        <button onclick="closeTeamModal()" class="text-xs font-medium px-2.5 py-1 rounded hi-subcard hover:opacity-80 cursor-pointer">Close</button>
      </div>

      <div class="grid grid-cols-4 gap-2 text-center text-xs">
        <div class="p-2.5 rounded hi-subcard">
          <div style="color: var(--hi-muted);">AdjEM</div>
          <div id="modal-em" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
        <div class="p-2.5 rounded hi-subcard">
          <div style="color: var(--hi-muted);">AdjO</div>
          <div id="modal-adjo" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
        <div class="p-2.5 rounded hi-subcard">
          <div style="color: var(--hi-muted);">AdjD</div>
          <div id="modal-adjd" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
        <div class="p-2.5 rounded hi-subcard">
          <div style="color: var(--hi-muted);">AdjT</div>
          <div id="modal-tempo" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-2 text-xs px-0.5" style="color: var(--hi-muted);">
        <span id="modal-ff" class="font-mono">—</span>
        <button onclick="sendModalTeamToSim()" class="font-medium hover:underline cursor-pointer" style="color: var(--hi-accent);">Open in Predictor →</button>
      </div>

      <div class="overflow-y-auto flex-1 border-t pt-2" style="border-color: var(--hi-border);">
        <table class="w-full text-left border-collapse text-xs">
          <thead style="color: var(--hi-muted); border-bottom: 1px solid var(--hi-border);">
            <tr>
              <th class="py-1.5 px-2 font-semibold">Date</th>
              <th class="py-1.5 px-2 font-semibold">Loc</th>
              <th class="py-1.5 px-2 font-semibold">Opponent</th>
              <th class="py-1.5 px-2 font-semibold">Result</th>
              <th class="py-1.5 px-2 font-semibold text-right">ORtg / DRtg</th>
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
    const HIST = SITE_DATA.history || { total_games: 0, correct: 0, win_pct: 0, mae: 0, buckets: [], days: [] };
    const TEAM_MAP = {};
    TEAMS.forEach(t => { TEAM_MAP[t.team] = t; });

    let modalTeamName = TEAMS[0].team;
    let activeSlateFilter = 'ALL';
    let simLoc = 'neutral';
    let usePrior = true;
    let histOutcomeFilter = 'ALL';
    let histViewRanks = false;

    function toggleTheme() {
      const root = document.documentElement;
      const isDark = root.classList.contains('dark');
      if (isDark) {
        root.classList.remove('dark');
        root.classList.add('light');
        document.getElementById('theme-btn').textContent = 'Dark';
      } else {
        root.classList.remove('light');
        root.classList.add('dark');
        document.getElementById('theme-btn').textContent = 'Light';
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
      renderRankingsTable();
      renderSlate();
      runMatchupSim();
    }

    function switchMainTab(tab) {
      ['rankings', 'slate', 'history', 'matchup', 'model'].forEach(t => {
        const btn = document.getElementById('nav-' + t);
        const pane = document.getElementById('tab-' + t);
        if (t === tab) {
          btn.style.borderBottom = '2px solid var(--hi-accent)';
          btn.style.color = 'var(--hi-text)';
          pane.classList.remove('hidden');
        } else {
          btn.style.borderBottom = '2px solid transparent';
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
        return `
        <tr class="hi-row cursor-pointer" onclick="openTeamModal('${r.team.replace(/'/g, "\\'")}')">
          <td class="py-2 px-3.5 tabular-nums text-xs font-mono" style="color: var(--hi-muted);">${v.rank}</td>
          <td class="py-2 px-3.5 font-semibold">
            ${r.team}${r.alt ? '<span title="High-Altitude Venue (+1.55 HCA)" class="ml-1.5 text-[10px] font-mono px-1 py-0.5 rounded hi-subcard" style="color: var(--hi-muted);">ALT</span>' : ''}
          </td>
          <td class="py-2 px-3 text-xs" style="color: var(--hi-muted);">${r.conf}</td>
          <td class="py-2 px-3 text-xs tabular-nums" style="color: var(--hi-muted);">${r.record}</td>
          <td class="py-2 px-3.5 text-right font-mono font-semibold tabular-nums" style="color: ${v.adj_em >= 0 ? 'var(--hi-pos)' : 'var(--hi-neg)'};">
            ${v.adj_em >= 0 ? '+' : ''}${v.adj_em.toFixed(2)}
          </td>
          <td class="py-2 px-3.5 text-right font-mono tabular-nums">
            ${v.adj_o.toFixed(1)} <span class="text-xs ml-0.5" style="color: var(--hi-muted);">${v.o_rk}</span>
          </td>
          <td class="py-2 px-3.5 text-right font-mono tabular-nums">
            ${v.adj_d.toFixed(1)} <span class="text-xs ml-0.5" style="color: var(--hi-muted);">${v.d_rk}</span>
          </td>
          <td class="py-2 px-3.5 text-right font-mono tabular-nums" style="color: var(--hi-muted);">${r.tempo.toFixed(1)}</td>
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
      document.getElementById('modal-sub').textContent = `${r.conf} · ${r.record} · T-Rank #${r.torvik_rk}`;
      document.getElementById('modal-em').textContent = `${v.adj_em >= 0 ? '+' : ''}${v.adj_em.toFixed(2)}`;
      document.getElementById('modal-em').style.color = v.adj_em >= 0 ? 'var(--hi-pos)' : 'var(--hi-neg)';
      document.getElementById('modal-adjo').textContent = `${v.adj_o.toFixed(1)} (${v.o_rk})`;
      document.getElementById('modal-adjd').textContent = `${v.adj_d.toFixed(1)} (${v.d_rk})`;
      document.getElementById('modal-tempo').textContent = r.tempo.toFixed(1);
      document.getElementById('modal-ff').textContent = `eFG ${r.efg}% · ORB ${r.orb}% · Opp ORB ${r.opp_orb}% · TOV ${r.tov}%`;

      const logTbody = document.getElementById('modal-logs-tbody');
      if (!r.logs || r.logs.length === 0) {
        logTbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center" style="color: var(--hi-muted);">No completed D-I games yet.</td></tr>`;
      } else {
        logTbody.innerHTML = r.logs.map(lg => `
          <tr class="hi-row">
            <td class="py-1.5 px-2 tabular-nums" style="color: var(--hi-muted);">${lg.date}</td>
            <td class="py-1.5 px-2">${lg.loc}</td>
            <td class="py-1.5 px-2 font-medium cursor-pointer hover:underline" onclick="openTeamModal('${lg.opp.replace(/'/g, "\\'")}')">
              #${lg.opp_rk} ${lg.opp}
            </td>
            <td class="py-1.5 px-2 font-semibold tabular-nums" style="color: ${lg.win ? 'var(--hi-pos)' : 'var(--hi-neg)'};">
              ${lg.win ? 'W' : 'L'} ${lg.score}
            </td>
            <td class="py-1.5 px-2 text-right font-mono tabular-nums" style="color: var(--hi-muted);">${lg.ortg} / ${lg.drtg}</td>
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
          ? 'background-color: var(--hi-text); color: var(--hi-surface);'
          : 'background-color: var(--hi-surface); color: var(--hi-muted); border: 1px solid var(--hi-border);';
        return `<button onclick="setSlateFilter('${b.key}')" style="${style}" class="px-3 py-1 text-xs font-medium rounded-md transition cursor-pointer">${b.label}</button>`;
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
        tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-xs" style="color: var(--hi-muted);">No games match this filter. Uncheck "Featured games only" to see all D-I games.</td></tr>`;
        return;
      }

      const mu = usePrior ? SITE_DATA.mu : SITE_DATA.mu_np;
      tbody.innerHTML = games.map(g => {
        const statusCell = g.is_final
          ? `<span class="text-xs font-semibold" style="color: var(--hi-pos);">${g.actual}</span>`
          : `<span class="text-xs" style="color: var(--hi-muted);">${g.neutral ? 'Neutral' : 'Home/Away'}</span>`;

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
            <td class="py-2.5 px-4 text-xs whitespace-nowrap" style="color: var(--hi-muted);">${g.date_label}</td>
            <td class="py-2.5 px-4">
              <span class="text-xs font-mono mr-1" style="color: var(--hi-muted);">${rk1}</span><span class="font-medium">${g.t1}</span>
              <span class="text-xs mx-1.5" style="color: var(--hi-muted);">${g.neutral ? 'vs.' : 'at'}</span>
              <span class="text-xs font-mono mr-1" style="color: var(--hi-muted);">${rk2}</span><span class="font-medium">${g.t2}</span>
            </td>
            <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${p1.toFixed(0)}–${p2.toFixed(0)}</td>
            <td class="py-2.5 px-4 text-right font-mono text-xs font-semibold tabular-nums">${fav} -${spr.toFixed(1)}</td>
            <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${g.vegas || '—'}</td>
            <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${favProb.toFixed(0)}%</td>
            <td class="py-2.5 px-4 text-right">${statusCell}</td>
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

    // ==================== HISTORICAL PERFORMANCE FUNCTIONS ====================
    function initHistoryTab() {
      if (!HIST.days || HIST.days.length === 0) return;
      const losses = HIST.total_games - HIST.correct;
      const recStr = `${HIST.correct}–${losses} (${HIST.win_pct.toFixed(1)}%)`;
      const atsStr = `${HIST.ats_w || 0}–${HIST.ats_l || 0} (${(HIST.ats_pct || 0).toFixed(1)}%)`;
      document.getElementById('hdr-record').textContent = recStr;
      document.getElementById('hdr-ats').textContent = atsStr;
      document.getElementById('hist-season-rec').textContent = recStr;
      document.getElementById('hist-season-ats').textContent = atsStr;
      document.getElementById('hist-season-mae').textContent = `${HIST.mae.toFixed(2)} pts`;

      const bGrid = document.getElementById('hist-buckets-grid');
      bGrid.innerHTML = HIST.buckets.map(b => `
        <div class="hi-subcard rounded p-2.5">
          <div class="flex items-center justify-between font-mono text-[11px]" style="color: var(--hi-muted);">
            <span>Prob ${b.bucket}</span>
            <span>${b.games}g</span>
          </div>
          <div class="font-mono font-bold text-sm mt-1 tabular-nums">${b.actual_pct.toFixed(1)}% won</div>
          <div class="text-[11px] font-mono tabular-nums" style="color: var(--hi-muted);">Exp ${b.expected_pct.toFixed(1)}% · ${b.correct}/${b.games}</div>
        </div>
      `).join('');

      const sel = document.getElementById('hist-date-select');
      sel.innerHTML = HIST.days.map((d, idx) => {
        const l = d.games_count - d.correct;
        return `<option value="${idx}">${d.label} · SU ${d.correct}–${l} · ATS ${d.ats_w || 0}–${d.ats_l || 0}</option>`;
      }).join('');
      sel.value = "0";

      setHistOutcomeFilter('ALL');
    }

    function setHistOutcomeFilter(filt) {
      histOutcomeFilter = filt;
      ['ALL', 'ATS_W', 'ATS_L', 'MISS'].forEach(k => {
        const btn = document.getElementById('hfilt-' + k);
        if (!btn) return;
        if (k === filt) {
          btn.style.backgroundColor = 'var(--hi-text)';
          btn.style.color = 'var(--hi-surface)';
        } else {
          btn.style.backgroundColor = 'var(--hi-surface)';
          btn.style.color = 'var(--hi-muted)';
          btn.style.border = '1px solid var(--hi-border)';
        }
      });
      renderHistoryDay();
    }

    function toggleHistMode() {
      histViewRanks = !histViewRanks;
      const btn = document.getElementById('hist-mode-btn');
      const picksCard = document.getElementById('hist-picks-card');
      const ranksCard = document.getElementById('hist-ranks-card');
      const filtGroup = document.getElementById('hist-filter-group');
      if (histViewRanks) {
        btn.textContent = 'View Daily Picks & Results';
        picksCard.classList.add('hidden');
        ranksCard.classList.remove('hidden');
        filtGroup.classList.add('hidden');
      } else {
        btn.textContent = 'View Pre-Game Top 40 Rankings';
        ranksCard.classList.add('hidden');
        picksCard.classList.remove('hidden');
        filtGroup.classList.remove('hidden');
      }
      renderHistoryDay();
    }

    function onSelectHistoryDate() {
      renderHistoryDay();
    }

    function renderHistoryDay() {
      if (!HIST.days || HIST.days.length === 0) return;
      const idx = parseInt(document.getElementById('hist-date-select').value || '0', 10);
      const day = HIST.days[idx] || HIST.days[0];
      const losses = day.games_count - day.correct;
      document.getElementById('hist-day-summary').textContent =
        `SU ${day.correct}–${losses} (${day.win_pct.toFixed(1)}%) · ATS ${day.ats_w || 0}–${day.ats_l || 0} (${(day.ats_pct || 0).toFixed(1)}%) · MAE ${day.mae.toFixed(2)} pts`;

      // Render Picks Table
      let picks = day.picks || [];
      if (histOutcomeFilter === 'MISS') picks = picks.filter(p => !p.hit);
      else if (histOutcomeFilter === 'ATS_W') picks = picks.filter(p => p.ats_res === 'W');
      else if (histOutcomeFilter === 'ATS_L') picks = picks.filter(p => p.ats_res === 'L');

      const pTbody = document.getElementById('hist-picks-tbody');
      if (picks.length === 0) {
        pTbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-xs" style="color: var(--hi-muted);">No games match this filter on ${day.label}.</td></tr>`;
      } else {
        pTbody.innerHTML = picks.map(p => {
          const badgeStyle = p.hit
            ? 'color: var(--hi-pos); background-color: var(--hi-surface-alt);'
            : 'color: var(--hi-neg); background-color: var(--hi-surface-alt);';
          let atsCell = '<span style="color: var(--hi-muted);">—</span>';
          if (p.ats_pick) {
            const atsColor = p.ats_res === 'W' ? 'var(--hi-pos)' : (p.ats_res === 'L' ? 'var(--hi-neg)' : 'var(--hi-muted)');
            atsCell = `<span class="font-semibold" style="color: ${atsColor};">${p.ats_res}</span> <span style="color: var(--hi-muted);">${p.ats_pick}</span>`;
          }
          return `
            <tr class="hi-row">
              <td class="py-2 px-3">
                <span class="text-[11px] font-mono font-bold px-1.5 py-0.5 rounded" style="${badgeStyle}">${p.hit ? 'HIT' : 'MISS'}</span>
              </td>
              <td class="py-2 px-3">
                <span class="text-xs font-mono mr-1" style="color: var(--hi-muted);">#${p.r1}</span><span class="font-medium">${p.t1}</span>
                <span class="text-xs mx-1.5" style="color: var(--hi-muted);">${p.neutral ? 'vs.' : 'at'}</span>
                <span class="text-xs font-mono mr-1" style="color: var(--hi-muted);">#${p.r2}</span><span class="font-medium">${p.t2}</span>
              </td>
              <td class="py-2 px-3 text-right font-mono text-xs font-semibold tabular-nums">${p.fav} -${p.spread.toFixed(1)}</td>
              <td class="py-2 px-3 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${p.vegas || '—'}</td>
              <td class="py-2 px-3 text-right font-mono text-xs tabular-nums">${atsCell}</td>
              <td class="py-2 px-3 text-right font-mono text-xs font-semibold tabular-nums">${p.winner} ${Math.max(p.p1, p.p2)}–${Math.min(p.p1, p.p2)}</td>
              <td class="py-2 px-3 text-right font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${p.err.toFixed(1)}</td>
            </tr>
          `;
        }).join('');
      }

      // Render Pre-Game Top 40 Rankings Snapshot
      document.getElementById('hist-ranks-title').textContent = `Pre-Game Top 40 Rankings Entering ${day.label} (${day.date})`;
      const rTbody = document.getElementById('hist-ranks-tbody');
      rTbody.innerHTML = (day.top40 || []).map(r => `
        <tr class="hi-row">
          <td class="py-2 px-3.5 font-mono text-xs tabular-nums" style="color: var(--hi-muted);">${r.rank}</td>
          <td class="py-2 px-3.5 font-semibold">${r.team}</td>
          <td class="py-2 px-3 text-xs" style="color: var(--hi-muted);">${r.conf}</td>
          <td class="py-2 px-3 text-xs font-mono tabular-nums" style="color: var(--hi-muted);">${r.record}</td>
          <td class="py-2 px-3.5 text-right font-mono font-semibold tabular-nums" style="color: ${r.adj_em >= 0 ? 'var(--hi-pos)' : 'var(--hi-neg)'};">
            ${r.adj_em >= 0 ? '+' : ''}${r.adj_em.toFixed(2)}
          </td>
          <td class="py-2 px-3.5 text-right font-mono tabular-nums">${r.adj_o.toFixed(1)}</td>
          <td class="py-2 px-3.5 text-right font-mono tabular-nums">${r.adj_d.toFixed(1)}</td>
          <td class="py-2 px-3.5 text-right font-mono tabular-nums" style="color: var(--hi-muted);">${r.tempo.toFixed(1)}</td>
        </tr>
      `).join('');
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
          btn.style.backgroundColor = 'var(--hi-text)';
          btn.style.color = 'var(--hi-surface)';
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
      document.getElementById('sim-total-sub').textContent = `Total ${(ptsA + ptsB).toFixed(1)} · ${estPoss.toFixed(1)} poss`;

      document.getElementById('sim-bar-a').style.width = `${probA.toFixed(1)}%`;
      document.getElementById('sim-bar-b').style.width = `${probB.toFixed(1)}%`;
      document.getElementById('sim-prob-a').textContent = `${a.team} ${probA.toFixed(1)}%`;
      document.getElementById('sim-prob-b').textContent = `${b.team} ${probB.toFixed(1)}%`;

      const baseDiff = (va.adj_em - vb.adj_em) * (estPoss / 100.0);
      const hcaPts = hcaA * (estPoss / 100.0);
      document.getElementById('sim-math-breakdown').innerHTML = `
        <span>Neutral efficiency: <strong style="color: var(--hi-text);">${baseDiff >= 0 ? a.team : b.team} +${Math.abs(baseDiff).toFixed(1)}</strong></span>
        <span>Court/Altitude: <strong style="color: var(--hi-text);">${Math.abs(hcaPts) < 0.05 ? 'Neutral' : (hcaPts > 0 ? a.team + ' +' + hcaPts.toFixed(1) : b.team + ' +' + Math.abs(hcaPts).toFixed(1))}</strong></span>
        <span>ORB%: <strong style="color: var(--hi-text);">${a.orb}% vs ${b.orb}%</strong></span>
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

      initHistoryTab();
      switchMainTab('rankings');
      setSimLoc('neutral');
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
print("Rendered clean editorial HodgesIndex UI (index.html):", len(final_html), "bytes")
