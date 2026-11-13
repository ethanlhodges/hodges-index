#!/usr/bin/env python3
"""
Renders a clean, minimalist, KenPom-inspired 2026-27 College Basketball Rankings site
from site_payload.json. Designed for calm typography, generous whitespace, and zero clutter.
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent
PAYLOAD_JSON = (DATA_DIR / "site_payload.json").read_text()
ARTIFACT_DIR = Path("/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/1e980916-ecae-478e-bedb-b2e0d94a61c3")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HodgesIndex · 2026–27 D-I Basketball</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    .tabular-nums { font-variant-numeric: tabular-nums; }
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 md:p-8">

  <div class="max-w-5xl mx-auto space-y-6">

    <!-- Minimalist Editorial Header -->
    <header class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-[var(--border)] pb-4">
      <div>
        <h1 class="text-xl md:text-2xl font-bold tracking-tight text-[var(--foreground)]">
          HodgesIndex
        </h1>
        <p class="text-xs text-[var(--muted-foreground)] mt-1">
          2026–27 D-I Tempo-Free Model · Updated <span id="hdr-date" class="text-[var(--foreground)] font-medium">—</span> ·
          <span id="hdr-games">—</span> games ·
          Prior weight <span id="hdr-prior" class="tabular-nums">—</span>
        </p>
      </div>

      <!-- Clean Underline Navigation -->
      <nav class="flex items-center gap-5 text-sm">
        <button onclick="switchMainTab('rankings')" id="nav-rankings" class="pb-1.5 font-semibold border-b-2 border-[var(--primary)] text-[var(--foreground)] transition">
          Rankings
        </button>
        <button onclick="switchMainTab('slate')" id="nav-slate" class="pb-1.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition">
          Games
        </button>
        <button onclick="switchMainTab('matchup')" id="nav-matchup" class="pb-1.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition">
          Predictor
        </button>
        <button onclick="switchMainTab('model')" id="nav-model" class="pb-1.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition">
          Methodology
        </button>
      </nav>
    </header>

    <!-- ==================== TAB 1: CLEAN FULL-WIDTH RANKINGS ==================== -->
    <section id="tab-rankings" class="space-y-4">
      <!-- Subtle Filter Bar -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2.5">
          <input id="rank-search" type="text" placeholder="Filter team..." oninput="renderRankingsTable()"
            class="px-3 py-1.5 text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] w-48 focus:outline-none focus:border-[var(--primary)]" />
          <select id="rank-conf" onchange="renderRankingsTable()"
            class="px-2.5 py-1.5 text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]">
            <option value="ALL">All Conferences</option>
          </select>
          <select id="rank-sort" onchange="renderRankingsTable()"
            class="px-2.5 py-1.5 text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]">
            <option value="adj_em">Sort by Overall (AdjEM)</option>
            <option value="adj_o">Sort by Offense (AdjO)</option>
            <option value="adj_d">Sort by Defense (AdjD)</option>
            <option value="tempo">Sort by Tempo (AdjT)</option>
          </select>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <label class="inline-flex items-center gap-1.5 text-xs text-[var(--muted-foreground)] cursor-pointer select-none">
            <input id="toggle-prior" type="checkbox" checked onchange="onTogglePrior()" class="rounded border-[var(--border)]" />
            <span>Include prior-season weighting</span>
          </label>
          <span id="rank-count-label" class="text-xs text-[var(--muted-foreground)]">Click any team for game log</span>
        </div>
      </div>

      <!-- Full-Width Table with Generous Breathing Room -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto max-h-[640px] overflow-y-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 bg-[var(--card)] border-b border-[var(--border)] text-xs text-[var(--muted-foreground)]">
              <tr>
                <th class="py-2.5 px-3.5 font-medium w-12">Rk</th>
                <th class="py-2.5 px-3.5 font-medium">Team</th>
                <th class="py-2.5 px-3 font-medium">Conf</th>
                <th class="py-2.5 px-3 font-medium">W–L</th>
                <th class="py-2.5 px-3.5 font-medium text-right" title="Adjusted Efficiency Margin">AdjEM</th>
                <th class="py-2.5 px-3.5 font-medium text-right" title="Adjusted Offensive Efficiency">AdjO</th>
                <th class="py-2.5 px-3.5 font-medium text-right" title="Adjusted Defensive Efficiency">AdjD</th>
                <th class="py-2.5 px-3.5 font-medium text-right" title="Adjusted Tempo">AdjT</th>
              </tr>
            </thead>
            <tbody id="rankings-tbody" class="divide-y divide-[var(--border)] text-sm"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 2: CLEAN DAILY GAMES LIST ==================== -->
    <section id="tab-slate" class="hidden space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div id="slate-filter-btns" class="flex flex-wrap items-center gap-2"></div>
        <label class="inline-flex items-center gap-2 text-xs text-[var(--muted-foreground)] cursor-pointer">
          <input id="slate-featured-only" type="checkbox" checked onchange="renderSlate()" class="rounded border-[var(--border)]" />
          <span>Featured matchups only (Top 60 teams)</span>
        </label>
      </div>

      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="border-b border-[var(--border)] text-xs text-[var(--muted-foreground)]">
              <tr>
                <th class="py-2.5 px-4 font-medium">Date</th>
                <th class="py-2.5 px-4 font-medium">Matchup</th>
                <th class="py-2.5 px-4 font-medium text-right">Projected Score</th>
                <th class="py-2.5 px-4 font-medium text-right">Model Line</th>
                <th class="py-2.5 px-4 font-medium text-right">Win Prob</th>
                <th class="py-2.5 px-4 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody id="slate-tbody" class="divide-y divide-[var(--border)] text-sm"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 3: MINIMALIST MATCHUP PREDICTOR ==================== -->
    <section id="tab-matchup" class="hidden max-w-2xl mx-auto space-y-5 pt-2">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6 shadow-sm space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-[var(--muted-foreground)] block mb-1.5">Team A</label>
            <select id="sim-a" onchange="runMatchupSim()" class="w-full text-sm rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] p-2.5"></select>
          </div>
          <div>
            <label class="text-xs text-[var(--muted-foreground)] block mb-1.5">Team B</label>
            <select id="sim-b" onchange="runMatchupSim()" class="w-full text-sm rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] p-2.5"></select>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="setSimLoc('neutral')" id="loc-neutral" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)]">Neutral Floor</button>
          <button onclick="setSimLoc('home_b')" id="loc-home_b" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]">At Team B</button>
          <button onclick="setSimLoc('home_a')" id="loc-home_a" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]">At Team A</button>
        </div>

        <div class="pt-4 border-t border-[var(--border)] space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <div id="sim-name-a" class="text-xs text-[var(--muted-foreground)]">—</div>
              <div id="sim-pts-a" class="text-3xl font-bold tabular-nums text-[var(--foreground)]">—</div>
            </div>
            <div class="text-center">
              <div id="sim-line-badge" class="text-sm font-semibold text-[var(--foreground)]">—</div>
              <div id="sim-total-sub" class="text-xs text-[var(--muted-foreground)] mt-0.5 tabular-nums">—</div>
            </div>
            <div class="text-right">
              <div id="sim-name-b" class="text-xs text-[var(--muted-foreground)]">—</div>
              <div id="sim-pts-b" class="text-3xl font-bold tabular-nums text-[var(--foreground)]">—</div>
            </div>
          </div>

          <div class="w-full h-2 bg-[var(--secondary)] rounded-full overflow-hidden flex">
            <div id="sim-bar-a" class="h-full bg-blue-500 transition-all duration-200" style="width: 50%"></div>
            <div id="sim-bar-b" class="h-full bg-amber-500 transition-all duration-200" style="width: 50%"></div>
          </div>

          <div class="flex justify-between text-xs text-[var(--muted-foreground)] tabular-nums">
            <span id="sim-prob-a">—</span>
            <span id="sim-prob-b">—</span>
          </div>

          <div id="sim-math-breakdown" class="pt-3 border-t border-[var(--border)] flex flex-col sm:flex-row justify-between gap-2 text-xs text-[var(--muted-foreground)]"></div>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 4: METHODOLOGY BLURB ==================== -->
    <section id="tab-model" class="hidden max-w-3xl mx-auto">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6 md:p-8 shadow-sm space-y-5 text-sm leading-relaxed">
        <h2 class="text-lg font-bold text-[var(--foreground)]">How These Rankings Work</h2>
        <p class="text-[var(--muted-foreground)]">
          These ratings measure how many points per 100 possessions a college basketball team would outscore an average Division I opponent on a neutral court (<strong>Adjusted Efficiency Margin</strong>, or <code class="text-xs bg-[var(--secondary)] px-1 py-0.5 rounded">AdjEM</code>). Every day, our model ingests every completed D-I box score and solves a simultaneous <strong>Weighted Ridge Regression</strong> across all 365 teams to separate true team quality from schedule strength and home-court advantage.
        </p>
        <ul class="space-y-3 text-[var(--muted-foreground)] list-disc pl-5">
          <li><strong class="text-[var(--foreground)]">Tempo-Free & Possession-Weighted:</strong> Every game is converted into points per 100 possessions (<code class="text-xs">AdjO</code> for offense, <code class="text-xs">AdjD</code> for defense) and weighted by possessions. A separate Ridge solve computes opponent-adjusted pace (<code class="text-xs">AdjT</code>).</li>
          <li><strong class="text-[var(--foreground)]">3-Point Luck Filtering:</strong> Using Empirical Bayes shrinkage toward the 34.0% D-I average, we regress 15% of single-game 3-point shooting variance back to each team's baseline so hot or cold shooting nights don't distort long-term ratings.</li>
          <li><strong class="text-[var(--foreground)]">Garbage-Time Cap & Recency:</strong> Blowouts beyond 35 points per 100 possessions receive diminishing returns (25% slope), while a gentle daily decay (<code class="text-xs">0.9975/day</code>) gives slightly more weight to recent form.</li>
          <li><strong class="text-[var(--foreground)]">Fading Preseason Priors:</strong> Early-season ratings are anchored toward a regressed prior from last season that automatically fades to <strong>zero</strong> once teams reach 14 games played in January—meaning conference play and March Madness are 100% earned on this season's court.</li>
          <li><strong class="text-[var(--foreground)]">Altitude-Aware Home Court:</strong> Beyond standard home-court advantage (+4.0 pts/100 possessions), our model learns a dedicated elevation boost (+1.55 pts/100) for high-altitude Mountain West and Big 12 venues.</li>
        </ul>
        <p class="text-xs text-[var(--muted-foreground)] pt-2 border-t border-[var(--border)]">
          Every hyperparameter was selected via chronological walk-forward backtesting across 5,500+ out-of-sample D-I games (70.7% straight-up winner accuracy, 9.03-point Jan–Apr spread MAE, and 0.5476 log-loss).
        </p>
      </div>
    </section>

  </div>

  <!-- Clean Slide-Over Modal for Team Resume (Opens on row click) -->
  <div id="team-modal" class="hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4" onclick="if(event.target===this) closeTeamModal()">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl max-w-xl w-full p-5 shadow-xl space-y-4 max-h-[85vh] flex flex-col">
      <div class="flex items-start justify-between border-b border-[var(--border)] pb-3">
        <div>
          <div class="flex items-center gap-2">
            <span id="modal-rk" class="text-xs font-bold px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--foreground)]">#1</span>
            <h3 id="modal-name" class="text-lg font-bold text-[var(--foreground)]">—</h3>
          </div>
          <p id="modal-sub" class="text-xs text-[var(--muted-foreground)] mt-1">—</p>
        </div>
        <button onclick="closeTeamModal()" class="text-xs px-2.5 py-1 rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]">Close</button>
      </div>

      <div class="grid grid-cols-4 gap-2 text-center text-xs">
        <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)]">
          <div class="text-[var(--muted-foreground)]">AdjEM</div>
          <div id="modal-em" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
        <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)]">
          <div class="text-[var(--muted-foreground)]">AdjO</div>
          <div id="modal-adjo" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
        <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)]">
          <div class="text-[var(--muted-foreground)]">AdjD</div>
          <div id="modal-adjd" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
        <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--border)]">
          <div class="text-[var(--muted-foreground)]">AdjT</div>
          <div id="modal-tempo" class="font-mono font-bold text-sm mt-0.5">—</div>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs text-[var(--muted-foreground)] px-1">
        <span id="modal-ff">—</span>
        <button onclick="sendModalTeamToSim()" class="text-[var(--primary)] font-medium hover:underline">Simulate matchup →</button>
      </div>

      <div class="overflow-y-auto flex-1 border-t border-[var(--border)] pt-2">
        <table class="w-full text-left border-collapse text-xs">
          <thead class="text-[var(--muted-foreground)] border-b border-[var(--border)]">
            <tr>
              <th class="py-1.5 px-2 font-medium">Date</th>
              <th class="py-1.5 px-2 font-medium">Loc</th>
              <th class="py-1.5 px-2 font-medium">Opponent</th>
              <th class="py-1.5 px-2 font-medium">Result</th>
              <th class="py-1.5 px-2 font-medium text-right">ORtg / DRtg</th>
            </tr>
          </thead>
          <tbody id="modal-logs-tbody" class="divide-y divide-[var(--border)]"></tbody>
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
      ['rankings', 'slate', 'matchup', 'model'].forEach(t => {
        const btn = document.getElementById('nav-' + t);
        const pane = document.getElementById('tab-' + t);
        if (t === tab) {
          btn.className = 'pb-1.5 font-semibold border-b-2 border-[var(--primary)] text-[var(--foreground)] transition';
          pane.classList.remove('hidden');
        } else {
          btn.className = 'pb-1.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition';
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

      document.getElementById('rank-count-label').textContent = `${rows.length} teams · Click any row for game log`;

      const tbody = document.getElementById('rankings-tbody');
      tbody.innerHTML = rows.map(r => {
        const v = tv(r);
        return `
        <tr class="hover:bg-[var(--secondary)]/50 cursor-pointer transition" onclick="openTeamModal('${r.team.replace(/'/g, "\\'")}')">
          <td class="py-2.5 px-3.5 tabular-nums text-[var(--muted-foreground)] font-medium">${v.rank}</td>
          <td class="py-2.5 px-3.5 font-semibold text-[var(--foreground)]">
            ${r.team}${r.alt ? '<span title="High-Altitude Venue" class="ml-1 text-xs text-amber-500">▲</span>' : ''}
          </td>
          <td class="py-2.5 px-3 text-xs text-[var(--muted-foreground)]">${r.conf}</td>
          <td class="py-2.5 px-3 text-xs tabular-nums text-[var(--muted-foreground)]">${r.record}</td>
          <td class="py-2.5 px-3.5 text-right font-mono font-semibold tabular-nums ${v.adj_em >= 0 ? 'text-emerald-500' : 'text-rose-500'}">
            ${v.adj_em >= 0 ? '+' : ''}${v.adj_em.toFixed(2)}
          </td>
          <td class="py-2.5 px-3.5 text-right font-mono tabular-nums">
            ${v.adj_o.toFixed(1)} <span class="text-xs text-[var(--muted-foreground)]">${v.o_rk}</span>
          </td>
          <td class="py-2.5 px-3.5 text-right font-mono tabular-nums">
            ${v.adj_d.toFixed(1)} <span class="text-xs text-[var(--muted-foreground)]">${v.d_rk}</span>
          </td>
          <td class="py-2.5 px-3.5 text-right font-mono tabular-nums text-[var(--muted-foreground)]">${r.tempo.toFixed(1)}</td>
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
      document.getElementById('modal-adjo').textContent = `${v.adj_o.toFixed(1)} (#${v.o_rk})`;
      document.getElementById('modal-adjd').textContent = `${v.adj_d.toFixed(1)} (#${v.d_rk})`;
      document.getElementById('modal-tempo').textContent = r.tempo.toFixed(1);
      document.getElementById('modal-ff').textContent = `eFG ${r.efg}% · ORB ${r.orb}% · Opp ORB ${r.opp_orb}% · TOV ${r.tov}%`;

      const logTbody = document.getElementById('modal-logs-tbody');
      if (!r.logs || r.logs.length === 0) {
        logTbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-[var(--muted-foreground)]">No completed D-I games yet.</td></tr>`;
      } else {
        logTbody.innerHTML = r.logs.map(lg => `
          <tr class="hover:bg-[var(--secondary)]/40">
            <td class="py-1.5 px-2 tabular-nums text-[var(--muted-foreground)]">${lg.date}</td>
            <td class="py-1.5 px-2">${lg.loc}</td>
            <td class="py-1.5 px-2 font-medium cursor-pointer hover:underline" onclick="openTeamModal('${lg.opp.replace(/'/g, "\\'")}')">
              #${lg.opp_rk} ${lg.opp}
            </td>
            <td class="py-1.5 px-2 font-semibold tabular-nums ${lg.win ? 'text-emerald-500' : 'text-rose-500'}">
              ${lg.win ? 'W' : 'L'} ${lg.score}
            </td>
            <td class="py-1.5 px-2 text-right font-mono tabular-nums text-[var(--muted-foreground)]">${lg.ortg} / ${lg.drtg}</td>
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
        const cls = isActive
          ? 'px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--card)] border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]';
        return `<button onclick="setSlateFilter('${b.key}')" class="${cls}">${b.label}</button>`;
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
        tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-xs text-[var(--muted-foreground)]">No games match this filter. Uncheck "Featured matchups only" to see all D-I games.</td></tr>`;
        return;
      }

      const mu = usePrior ? SITE_DATA.mu : SITE_DATA.mu_np;
      tbody.innerHTML = games.map(g => {
        const statusCell = g.is_final
          ? `<span class="text-xs font-semibold text-emerald-500">${g.actual}</span>`
          : `<span class="text-xs text-[var(--muted-foreground)]">${g.neutral ? 'Neutral' : 'Home/Away'}</span>`;

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
          <tr onclick="openMatchupFromSlate('${g.t1.replace(/'/g, "\\'")}', '${g.t2.replace(/'/g, "\\'")}', ${g.neutral})" class="hover:bg-[var(--secondary)]/50 cursor-pointer transition">
            <td class="py-2.5 px-4 text-xs text-[var(--muted-foreground)] whitespace-nowrap">${g.date_label}</td>
            <td class="py-2.5 px-4">
              <span class="font-medium text-[var(--foreground)]">#${rk1} ${g.t1}</span>
              <span class="text-xs text-[var(--muted-foreground)] mx-1">${g.neutral ? 'vs.' : 'at'}</span>
              <span class="font-medium text-[var(--foreground)]">#${rk2} ${g.t2}</span>
            </td>
            <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums text-[var(--muted-foreground)]">${p1.toFixed(0)}–${p2.toFixed(0)}</td>
            <td class="py-2.5 px-4 text-right font-mono text-xs font-semibold tabular-nums text-[var(--foreground)]">${fav} -${spr.toFixed(1)}</td>
            <td class="py-2.5 px-4 text-right font-mono text-xs tabular-nums text-[var(--muted-foreground)]">${favProb.toFixed(0)}%</td>
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

    function setSimLoc(loc) {
      simLoc = loc;
      ['neutral', 'home_b', 'home_a'].forEach(l => {
        const btn = document.getElementById('loc-' + l);
        btn.className = l === loc
          ? 'px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--secondary)] text-[var(--secondary-foreground)]';
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
        <span>Efficiency edge: <strong class="text-[var(--foreground)]">${baseDiff >= 0 ? a.team : b.team} +${Math.abs(baseDiff).toFixed(1)}</strong></span>
        <span>HCA: <strong class="text-[var(--foreground)]">${Math.abs(hcaPts) < 0.05 ? 'Neutral' : (hcaPts > 0 ? a.team + ' +' + hcaPts.toFixed(1) : b.team + ' +' + Math.abs(hcaPts).toFixed(1))}</strong></span>
        <span>ORB%: <strong class="text-[var(--foreground)]">${a.orb}% vs ${b.orb}%</strong></span>
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
print("Rendered HodgesIndex site (index.html):", len(final_html), "bytes")
