/* The Collatz mini-story (Problem 14): one simple rule, wild trajectories, an open problem,
   and the shortcut that makes the search cheap — remember what you already know.
   Problem 14's own answer (the start below one million with the longest chain) is never shown;
   the scatter stops at 10,000. Registers itself on window.DECK_PARTS (data-viz="collatz"). */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const VIEW = 700;
  const SCATTER = 10_000;
  const BARS = 40;

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
  const fmt = n => n.toLocaleString('en-GB');
  const next = n => (n % 2 === 0 ? n / 2 : 3 * n + 1);
  const chain = n => { const s = [n]; while (n !== 1) { n = next(n); s.push(n); } return s; };
  const steps = n => chain(n).length - 1;
  /* Steps until the chain first drops below its start: all a memo-backed search must compute. */
  const fresh = n => { if (n < 2) return 0; let m = n, k = 0; while (m >= n) { m = next(m); k++; } return k; };

  const M = { l: 70, r: 30, t: 40, b: 60 };
  const W = VIEW - M.l - M.r, H = VIEW - M.t - M.b;

  /* Axes for a chart with x in [0, xMax] and y in [0, yMax]; returns the scale functions. */
  function axes(g, xMax, yMax, xTicks, yTicks, xLabel) {
    const x = v => M.l + (v / xMax) * W, y = v => M.t + H - (v / yMax) * H;
    const a = el('g', { class: 'axis' }, g);
    el('line', { x1: M.l, x2: M.l + W, y1: y(0), y2: y(0) }, a);
    for (const v of yTicks) {
      text(a, M.l - 12, y(v) + 6, fmt(v), { 'text-anchor': 'end' });
      if (v) el('line', { x1: M.l, x2: M.l + W, y1: y(v), y2: y(v), opacity: 0.35 }, a);
    }
    for (const v of xTicks) text(a, x(v), y(0) + 30, fmt(v), { 'text-anchor': 'middle' });
    text(a, M.l + W, y(0) + 54, xLabel, { 'text-anchor': 'end', class: 'chart-label' });
    return { x, y };
  }

  function lineChart(g, seq, yMax, yTicks, xTicks, labelPoints) {
    const { x, y } = axes(g, seq.length - 1, yMax, xTicks, yTicks, 'Step');
    const d = seq.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join('');
    el('path', { d, class: 'cz-line', pathLength: 1 }, g);
    if (labelPoints) {
      seq.forEach((v, i) => {
        el('circle', { cx: x(i), cy: y(v), r: 7, class: 'cz-point' }, g);
        const dip = i > 0 && i < seq.length - 1 && v < seq[i - 1] && v < seq[i + 1];
        const falling = i > 0 && v < seq[i - 1];
        text(g, x(i) + (falling && !dip ? 16 : 0), y(v) + (dip ? 36 : -18), String(v),
          { 'text-anchor': falling && !dip ? 'start' : 'middle', class: 'cz-value' });
      });
    }
    return { x, y };
  }

  function controller(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const tallyEl = slide.querySelector('[data-role="tally"]');
    const svg = el('svg', { viewBox: `0 0 ${VIEW} ${VIEW}`, role: 'img' }, box);
    const layers = [];
    const layer = name => { const g = el('g', { class: `cz-layer cz-${name}` }, svg); layers.push(g); return g; };
    const last = 5;
    let step = 0;

    // ---- 0: the rule, from 6
    const six = layer('six');
    lineChart(six, chain(6), 18, [0, 5, 10, 15], [0, 2, 4, 6, 8], true);

    // ---- 1: from 27, the famous wild ride
    const s27 = chain(27);
    const peakAt = s27.indexOf(Math.max(...s27));
    const ride = layer('ride');
    const r = lineChart(ride, s27, 10_000, [0, 2500, 5000, 7500, 10_000], [0, 25, 50, 75, 100], false);
    el('circle', { cx: r.x(peakAt), cy: r.y(s27[peakAt]), r: 9, class: 'cz-peak' }, ride);
    text(ride, r.x(peakAt) + 18, r.y(s27[peakAt]) + 8, `${fmt(s27[peakAt])}, at step ${peakAt}`, { class: 'cz-note' });

    // ---- 2–3: chain length for every start up to 10,000
    const cloud = layer('cloud');
    const lengths = Array.from({ length: SCATTER + 1 }, (_, n) => (n ? steps(n) : 0));
    const longest = lengths.indexOf(Math.max(...lengths));
    const c = axes(cloud, SCATTER, 280, [0, 2500, 5000, 7500, 10_000], [0, 70, 140, 210, 280], 'Starting number');
    const dots = el('g', { class: 'cz-dots' }, cloud);
    for (let n = 1; n <= SCATTER; n++) el('circle', { cx: c.x(n), cy: c.y(lengths[n]), r: 1.7 }, dots);
    for (const [n, label] of [[27, '27'], [longest, fmt(longest)]]) {
      el('circle', { cx: c.x(n), cy: c.y(lengths[n]), r: 8, class: 'cz-peak' }, cloud);
      text(cloud, c.x(n) + 14, c.y(lengths[n]) - 10, `${label}: ${lengths[n]} steps`, { class: 'cz-note' });
    }

    // ---- 4: what a memory saves, starts 1 to 40
    const memo = layer('memo');
    const b = axes(memo, BARS + 1, 120, [10, 20, 30, 40], [0, 30, 60, 90, 120], 'Starting number');
    const bw = (W / (BARS + 1)) * 0.7;
    let total = 0, computed = 0;
    for (let n = 1; n <= BARS; n++) {
      const all = steps(n), part = Math.min(fresh(n), all);
      total += all; computed += part;
      const bx = b.x(n) - bw / 2;
      el('rect', { x: bx, y: b.y(all), width: bw, height: b.y(0) - b.y(all), class: 'cz-bar-all' }, memo);
      const bar = el('rect', { x: bx, y: b.y(part), width: bw, height: b.y(0) - b.y(part), class: 'cz-bar-new' }, memo);
      bar.style.setProperty('--d', `${n * 30}ms`);
    }
    const memoTally = `For 1 to ${BARS}: ${fmt(computed)} steps worked out instead of ${fmt(total)}.`;

    // ---- 5: below one million (counted offline: too slow to recount on every page load)
    const million = layer('million');
    const ROWS = [['One step at a time', 131_434_272, 'cz-bar-all'], ['With a memory', 5_226_259, 'cz-bar-new']];
    ROWS.forEach(([label, value, cls], i) => {
      const y0 = 200 + i * 190;
      text(million, M.l, y0, label, { class: 'cz-bar-label' });
      el('rect', { x: M.l, y: y0 + 22, width: Math.max(6, (value / ROWS[0][1]) * W), height: 56, rx: 4, class: cls }, million);
      text(million, M.l, y0 + 118, `${fmt(value)} steps`, { class: 'cz-bar-value' });
    });

    const CAPTIONS = [
      ['One rule, applied again and again.',
        'If the number is even, halve it. If it’s odd, triple it and add one. Starting from 6, it reaches 1 in eight steps.'],
      ['Start at 27, and hold on.',
        `It climbs as high as ${fmt(s27[peakAt])} before falling back to 1, ${s27.length - 1} steps later.`],
      ['Every start up to 10,000.',
        'Each dot is one starting number, placed by how many steps it takes to reach 1. Problem 14 asks the same question up to a million.'],
      ['Does every number reach 1?',
        'Nobody knows. Computers have checked every start up to about 3 × 10²⁰, but no one has proved it. It’s called the Collatz conjecture.'],
      ['Remember what you already know.',
        'Check the starting numbers in order. Once a chain drops below its start, the rest of its length is already known, so stop counting.'],
      ['Up to a million: 25× less work.',
        'The same answer either way. The memory just stops us walking the same paths twice.'],
    ];
    const visible = [six, ride, cloud, cloud, memo, million];

    function show(s, animate) {
      step = s;
      const moving = animate && !reduceMotion;
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      tallyEl.textContent = s === 4 ? memoTally : '';
      for (const g of layers) g.classList.remove('on', 'play');
      void box.getBoundingClientRect();     // restart animations on replay
      visible[s].classList.add('on');
      if (moving) visible[s].classList.add('play');
      cloud.classList.toggle('muted', s === 3);
    }

    return {
      enter(direction) { show(direction < 0 ? last : 0, direction >= 0); },
      leave() {},
      next() { if (step >= last) return false; show(step + 1, true); return true; },
      prev() { if (step <= 0) return false; show(step - 1, false); return true; },
      replay() { show(step, true); },
      jump(s) { show(Math.max(0, Math.min(last, s)), false); },
    };
  }

  window.DECK_PARTS = window.DECK_PARTS || {};
  window.DECK_PARTS.collatz = controller;
})();
