/* Eleven Years of Puzzles — navigation and the data-driven slides.
   Data comes from window.HISTORY (data/history.js, built by build_data.py). */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const DAY = 86400000;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------------------------------------------------------------- data

  const raw = (window.HISTORY && window.HISTORY.problems) || [];
  const problems = raw.map(([n, title, level, pct, solvers, solved, date]) => ({
    n, title,
    level: Number.isInteger(level) ? level : null,
    pct: Number.isInteger(pct) ? pct : null,
    solvers: Number.isInteger(solvers) ? solvers : null,
    solved,
    date: date ? new Date(date) : null,
  }));
  const byNumber = new Map(problems.map(p => [p.n, p]));
  const solves = problems.filter(p => p.solved && p.date).sort((a, b) => a.date - b.date || a.n - b.n);
  const generated = window.HISTORY ? new Date(window.HISTORY.generated) : new Date();

  /* Difficulty bucket 1–5 by the site's percentage, as the web front end shades its grid. */
  const heat = p => (p.pct ? 1 + Math.min(Math.floor((p.pct - 1) / 20), 4) : 1);

  /* The story's chapters: the author's framing; the counts come from the data. */
  const CHAPTERS = [
    { name: 'The spark', from: '2015-01-01', to: '2016-01-01', anchor: 'start' },
    { name: 'The first push', from: '2019-01-01', to: '2021-01-01', anchor: 'start' },
    { name: 'The return', from: '2025-01-01', to: '2026-01-01', anchor: 'end' },
    { name: 'The surge', from: '2026-01-01', to: '2100-01-01', anchor: 'start' },
  ];

  // ---------------------------------------------------------------- helpers

  const el = (name, attrs = {}, parent = null) => {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  };
  const text = (parent, x, y, content, attrs = {}) => {
    const node = el('text', { x, y, ...attrs }, parent);
    node.textContent = content;
    return node;
  };
  const svgRoot = (container, w, h, aspect = 'xMidYMid meet') => {
    container.replaceChildren();
    return el('svg', { viewBox: `0 0 ${w} ${h}`, preserveAspectRatio: aspect, role: 'img' }, container);
  };
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const fmtDay = d => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  const fmtLongDay = d => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  const fmtMonth = d => d.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
  const fmtInt = n => n.toLocaleString('en-GB');
  const fmtGap = days => (days >= 365
    ? `${(days / 365.25).toFixed(1)} years pass`
    : `${Math.round(days / 30.44)} months pass`);
  const WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'];
  const word = n => (n >= 0 && n < WORDS.length ? WORDS[n] : String(n));

  // ---------------------------------------------------------------- the grid

  const COLS = 50, PITCH = 26, CELL = 22;

  /* Draw every problem as a cell; return {svg, cells: Map(number → rect)}. */
  function drawGrid(container, aspect) {
    const rows = Math.ceil(problems.length / COLS);
    const svg = svgRoot(container, COLS * PITCH, rows * PITCH, aspect);
    svg.setAttribute('aria-label', `${problems.length} problems, ${solves.length} solved`);
    const cells = new Map();
    problems.forEach((p, i) => {
      const rect = el('rect', {
        x: (i % COLS) * PITCH, y: Math.floor(i / COLS) * PITCH,
        width: CELL, height: CELL, rx: 3, class: 'cell',
      }, svg);
      const title = el('title', {}, rect);
      title.textContent = `Problem ${p.n}: ${p.title}`;
      cells.set(p.n, rect);
    });
    return { svg, cells };
  }

  const light = (rect, p, animate) => {
    rect.setAttribute('class', `cell h${heat(p)}${animate ? ' lit' : ''}`);
  };

  function titleGrid(slide) {
    const { cells } = drawGrid(slide.querySelector('.title-grid'), 'xMidYMid slice');
    for (const p of solves) light(cells.get(p.n), p, false);
  }

  // ---------------------------------------------------------------- timeline playback

  let playToken = 0;

  function timelineFinal(slide) {
    const { cells } = drawGrid(slide.querySelector('[data-role="grid"]'));
    for (const p of solves) light(cells.get(p.n), p, false);
    const last = solves[solves.length - 1];
    slide.querySelector('[data-role="date"]').textContent = last ? fmtDay(last.date) : '';
    slide.querySelector('[data-role="count"]').textContent = `${solves.length} solved`;
    return cells;
  }

  async function timelinePlay(slide) {
    const token = ++playToken;
    const cells = drawGrid(slide.querySelector('[data-role="grid"]')).cells;
    const dateEl = slide.querySelector('[data-role="date"]');
    const countEl = slide.querySelector('[data-role="count"]');
    const interlude = slide.querySelector('[data-role="interlude"]');
    interlude.classList.remove('show');
    if (reduceMotion || !solves.length) { timelineFinal(slide); return; }
    dateEl.textContent = fmtDay(solves[0].date);
    countEl.textContent = '0 solved';
    await sleep(700);
    for (let i = 0; i < solves.length; i++) {
      if (token !== playToken) return;
      const p = solves[i];
      light(cells.get(p.n), p, true);
      dateEl.textContent = fmtDay(p.date);
      countEl.textContent = `${i + 1} solved`;
      const next = solves[i + 1];
      if (!next) break;
      const gap = (next.date - p.date) / DAY;
      if (gap > 120) {
        await sleep(500);
        if (token !== playToken) return;
        interlude.textContent = fmtGap(gap);
        interlude.classList.add('show');
        await sleep(1900);
        interlude.classList.remove('show');
        await sleep(350);
      } else {
        await sleep(gap < 1 ? 28 : 55);
      }
    }
  }

  // ---------------------------------------------------------------- cumulative chart

  function cumulative(slide) {
    const W = 1360, H = 600, M = { l: 64, r: 24, t: 24, b: 110 };
    const svg = svgRoot(slide.querySelector('[data-role="chart"]'), W, H);
    svg.setAttribute('aria-label', 'Problems solved over time');
    if (!solves.length) return;
    const t0 = new Date('2015-01-01').getTime();
    const t1 = Math.max(generated.getTime(), solves[solves.length - 1].date.getTime()) + 60 * DAY;
    const yMax = Math.ceil(solves.length / 50) * 50;
    const x = t => M.l + ((t - t0) / (t1 - t0)) * (W - M.l - M.r);
    const y = v => H - M.b - (v / yMax) * (H - M.t - M.b);

    // the long pauses: any stretch of more than a year without a solve
    for (let i = 0; i + 1 < solves.length; i++) {
      const a = solves[i].date.getTime(), b = solves[i + 1].date.getTime();
      const days = (b - a) / DAY;
      if (days < 365) continue;
      el('rect', { x: x(a), y: M.t, width: x(b) - x(a), height: H - M.t - M.b, class: 'gap-band' }, svg);
      if (x(b) - x(a) > 150) {
        text(svg, (x(a) + x(b)) / 2, M.t + 60, `${(days / 365.25).toFixed(1)} years`,
          { class: 'gap-label', 'text-anchor': 'middle' });
      }
    }

    // axes
    const axis = el('g', { class: 'axis' }, svg);
    el('line', { x1: M.l, x2: W - M.r, y1: y(0), y2: y(0) }, axis);
    for (let v = 0; v <= yMax; v += 50) {
      text(axis, M.l - 14, y(v) + 6, String(v), { 'text-anchor': 'end' });
      if (v) el('line', { x1: M.l, x2: W - M.r, y1: y(v), y2: y(v), opacity: 0.35 }, axis);
    }
    for (let year = 2015; year <= new Date(t1).getFullYear(); year++) {
      const tx = x(new Date(`${year}-01-01`).getTime());
      el('line', { x1: tx, x2: tx, y1: y(0), y2: y(0) + 8 }, axis);
      text(axis, tx + 4, y(0) + 30, String(year));
    }

    // the step line and its area
    let d = `M${x(t0)},${y(0)}`;
    solves.forEach((p, i) => { d += `H${x(p.date.getTime())}V${y(i + 1)}`; });
    d += `H${x(t1)}`;
    el('path', { d: `${d}V${y(0)}H${x(t0)}Z`, class: 'chart-area' }, svg);
    el('path', { d, class: 'chart-line' }, svg);

    // milestones
    for (const k of [100, 200, 300, 400, 500]) {
      if (k > solves.length) break;
      const p = solves[k - 1], cx = x(p.date.getTime()), cy = y(k);
      const g = el('g', { class: 'milestone' }, svg);
      el('circle', { cx, cy, r: 7 }, g);
      text(g, cx - 16, cy + 6, `No. ${k}, ${fmtMonth(p.date)}`, { 'text-anchor': 'end' });
    }

    // chapters, bracketed under the axis
    const by = y(0) + 56;
    for (const c of CHAPTERS) {
      const from = new Date(c.from).getTime(), to = new Date(c.to).getTime();
      const inside = solves.filter(p => p.date.getTime() >= from && p.date.getTime() < to);
      if (!inside.length) continue;
      const a = x(inside[0].date.getTime()), b = Math.max(x(inside[inside.length - 1].date.getTime()), a + 4);
      el('path', { d: `M${a},${by - 10}V${by - 4}H${b}V${by - 10}`, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 2 }, svg);
      const tx = c.anchor === 'end' ? b : a;
      text(svg, tx, by + 24, c.name, { class: 'chapter-label', 'text-anchor': c.anchor });
      text(svg, tx, by + 48, `${inside.length} solved`, { class: 'chapter-sub', 'text-anchor': c.anchor });
    }
  }

  // ---------------------------------------------------------------- difficulty staircase

  function staircase(slide) {
    const W = 1360, H = 600, M = { l: 64, r: 24, t: 24, b: 64 };
    const svg = svgRoot(slide.querySelector('[data-role="chart"]'), W, H);
    svg.setAttribute('aria-label', 'Problems solved at each difficulty level');
    const levels = problems.filter(p => p.level !== null).map(p => p.level);
    if (!levels.length) return;
    const maxLevel = Math.max(...levels);
    const total = Array(maxLevel + 1).fill(0), done = Array(maxLevel + 1).fill(0);
    for (const p of problems) {
      if (p.level === null) continue;
      total[p.level]++;
      if (p.solved) done[p.level]++;
    }
    const yMax = Math.ceil(Math.max(...total) / 10) * 10;
    const slot = (W - M.l - M.r) / (maxLevel + 1), bw = slot * 0.72;
    const y = v => H - M.b - (v / yMax) * (H - M.t - M.b);
    const axis = el('g', { class: 'axis' }, svg);
    for (let v = 0; v <= yMax; v += 10) {
      text(axis, M.l - 14, y(v) + 6, String(v), { 'text-anchor': 'end' });
      el('line', { x1: M.l, x2: W - M.r, y1: y(v), y2: y(v), opacity: v ? 0.35 : 1 }, axis);
    }
    for (let lv = 0; lv <= maxLevel; lv++) {
      const bx = M.l + lv * slot + (slot - bw) / 2;
      el('rect', { x: bx, y: y(total[lv]), width: bw, height: y(0) - y(total[lv]), rx: 2, class: 'bar-total' }, svg);
      if (done[lv]) {
        const bucket = 1 + Math.min(Math.floor((lv / (maxLevel + 1)) * 5), 4);
        el('rect', { x: bx, y: y(done[lv]), width: bw, height: y(0) - y(done[lv]), rx: 2, class: `cell h${bucket}` }, svg);
      }
      const t = el('title', {}, svg.lastChild);
      t.textContent = `Level ${lv}: ${done[lv]} of ${total[lv]} solved`;
      if (lv % 5 === 0) text(axis, bx + bw / 2, y(0) + 30, String(lv), { 'text-anchor': 'middle' });
    }
    text(svg, W - M.r, y(0) + 56, 'Difficulty level', { class: 'chart-label', 'text-anchor': 'end' });
  }

  // ---------------------------------------------------------------- rarity

  function rarity(slide) {
    const container = slide.querySelector('[data-role="chart"]');
    const counted = solves.filter(p => p.solvers !== null);
    if (!counted.length) {
      container.innerHTML = '<div class="empty-state"><p>Solver counts appear after the next progress refresh.<br>'
        + 'Save the progress page, run <code>summary</code>, then <code>python docs/presentation/build_data.py</code>.</p></div>';
      return;
    }
    const first = byNumber.get(1);
    const rarest = [...counted].sort((a, b) => a.solvers - b.solvers).slice(0, 4);
    const rows = [first, ...rarest].filter(p => p && p.solvers !== null);
    const W = 1360, H = 600, labelW = 560, valueW = 150;
    const svg = svgRoot(container, W, H);
    svg.setAttribute('aria-label', 'How many people have solved each problem');
    const lo = 100, hi = 1e6;
    const bx = v => labelW + (Math.log10(Math.max(v, lo)) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo)) * (W - labelW - valueW);
    const rowH = Math.min(96, (H - 40) / rows.length);
    rows.forEach((p, i) => {
      const cy = 20 + i * rowH + rowH / 2;
      text(svg, labelW - 24, cy + 8, `${p.n}  ${p.title}`, { class: 'bar-label', 'text-anchor': 'end' });
      el('rect', { x: labelW, y: cy - 18, width: bx(p.solvers) - labelW, height: 36, rx: 3, class: `cell h${heat(p)}` }, svg);
      text(svg, bx(p.solvers) + 14, cy + 8, `${fmtInt(p.solvers)} people`, { class: 'bar-value' });
    });
  }

  // ---------------------------------------------------------------- statement numbers

  function fillStats() {
    const set = (key, value) => document.querySelectorAll(`[data-stat="${key}"]`)
      .forEach(node => { node.textContent = value; });
    if (!solves.length) return;
    set('first-date', fmtLongDay(solves[0].date));
    const nth = k => solves[k - 1] && solves[k - 1].date;
    if (nth(100)) set('years-to-100', word(Math.round((nth(100) - solves[0].date) / (365.25 * DAY))));
    if (nth(300)) set('months-100-to-300', word(Math.round((nth(300) - nth(100)) / (30.44 * DAY))));
  }

  // ---------------------------------------------------------------- deck

  const stage = document.getElementById('stage');
  const slides = [...stage.querySelectorAll('.slide')];
  const counter = document.getElementById('counter');
  const notes = document.getElementById('notes');
  let current = 0;

  const RENDER = { 'title-grid': titleGrid, timeline: timelineFinal, cumulative, staircase, rarity };
  const ENTER = { timeline: timelinePlay };
  /* Stepped slides (window.DECK_PARTS, e.g. sieve.js): next/prev step within the slide first. */
  const controllers = new Map();
  for (const s of slides) {
    const make = (window.DECK_PARTS || {})[s.dataset.viz];
    if (make) controllers.set(s, make(s));
  }

  function fit() {
    const scale = Math.min(window.innerWidth / 1600, window.innerHeight / 900);
    stage.style.transform = `scale(${scale})`;
  }

  function show(index, direction = 1) {
    controllers.get(slides[current])?.leave();
    current = Math.max(0, Math.min(slides.length - 1, index));
    playToken++;  // stop any playback on the slide we are leaving
    slides.forEach((s, i) => s.classList.toggle('active', i === current));
    const slide = slides[current];
    stage.dataset.theme = slide.dataset.theme || '';
    counter.textContent = `${current + 1} / ${slides.length}`;
    const n = slide.querySelector('.notes');
    notes.innerHTML = n ? n.innerHTML : '';
    history.replaceState(null, '', `#${current + 1}`);
    const enter = ENTER[slide.dataset.viz];
    if (enter) enter(slide);
    controllers.get(slide)?.enter(direction);
  }

  const forward = () => { if (!controllers.get(slides[current])?.next()) show(current + 1); };
  const back = () => { if (!controllers.get(slides[current])?.prev()) show(current - 1, -1); };
  const replay = () => {
    const ctrl = controllers.get(slides[current]);
    if (ctrl) ctrl.replay(); else show(current);
  };

  document.addEventListener('keydown', e => {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ': forward(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': back(); break;
      case 'Home': show(0); break;
      case 'End': show(slides.length - 1); break;
      case 'n': case 'N': notes.classList.toggle('show'); break;
      case 'r': case 'R': replay(); break;
      case 'f': case 'F':
        if (document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen().catch(() => {});
        break;
      default: return;
    }
    e.preventDefault();
  });
  document.getElementById('prev').addEventListener('click', back);
  document.getElementById('next').addEventListener('click', forward);
  document.getElementById('toggle-notes').addEventListener('click', () => notes.classList.toggle('show'));
  window.addEventListener('resize', fit);

  fillStats();
  slides.forEach(s => { const render = RENDER[s.dataset.viz]; if (render) render(s); });
  fit();
  // #12 opens slide 12; #12.3 also jumps a stepped slide to step 3
  const [slideNo, stepNo] = location.hash.slice(1).split('.').map(v => parseInt(v, 10));
  show((slideNo || 1) - 1);
  if (Number.isInteger(stepNo)) controllers.get(slides[current])?.jump(stepNo);
})();
