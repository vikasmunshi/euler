/* The lattice-paths mini-story (Problem 15): list the routes on a small grid, see listing
   explode, then count at each corner instead — and tilt the grid into Pascal's triangle.
   Problem 15's own answer (the 20 × 20 corner) is never shown: the method is worked on 6 × 6.
   Registers itself on window.DECK_PARTS; deck.js wires it to the slide data-viz="lattice". */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const VIEW = 700;
  const ROUTES_2x2 = ['RRDD', 'RDRD', 'RDDR', 'DRRD', 'DRDR', 'DDRR'];
  const SIZE = 6;                         // the counted grid: 6 × 6 squares, 7 × 7 corners
  const BIG = 20;                         // Problem 15's grid, drawn but never totalled

  const el = (name, attrs = {}, parent = null) => {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  };
  const binom = (n, k) => {
    let r = 1;
    for (let i = 1; i <= k; i++) r = (r * (n - k + i)) / i;
    return Math.round(r);
  };

  function controller(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const table = slide.querySelector('[data-role="table"]');
    const svg = el('svg', { viewBox: `0 0 ${VIEW} ${VIEW}`, role: 'img' }, box);
    const last = 5;
    let step = 0;

    // ---- layer 1: the six routes across a 2 × 2 grid, as small multiples
    const routes = el('g', { class: 'lp-layer lp-routes' }, svg);
    const M = 170, U = 60;                // mini-grid pitch and unit
    ROUTES_2x2.forEach((route, i) => {
      const ox = 80 + (i % 3) * (M + 30), oy = 170 + Math.floor(i / 3) * (M + 50);
      for (let k = 0; k <= 2; k++) {
        el('line', { x1: ox, y1: oy + k * U, x2: ox + 2 * U, y2: oy + k * U, class: 'lp-grid' }, routes);
        el('line', { x1: ox + k * U, y1: oy, x2: ox + k * U, y2: oy + 2 * U, class: 'lp-grid' }, routes);
      }
      let x = ox, y = oy, d = `M${x},${y}`;
      for (const move of route) {
        if (move === 'R') x += U; else y += U;
        d += `L${x},${y}`;
      }
      const path = el('path', { d, class: 'lp-route', pathLength: 1 }, routes);
      path.style.setProperty('--d', `${i * 380}ms`);
      el('circle', { cx: ox, cy: oy, r: 7, class: 'lp-end' }, routes);
      el('circle', { cx: ox + 2 * U, cy: oy + 2 * U, r: 7, class: 'lp-end' }, routes);
    });

    // ---- layer 2: the 6 × 6 grid, counted corner by corner (tilts into Pascal's triangle)
    const counted = el('g', { class: 'lp-layer lp-counted' }, svg);
    const tilt = el('g', { class: 'lp-tilt' }, counted);
    const P = 92, O = (VIEW - SIZE * P) / 2;
    for (let k = 0; k <= SIZE; k++) {
      el('line', { x1: O, y1: O + k * P, x2: O + SIZE * P, y2: O + k * P, class: 'lp-grid' }, tilt);
      el('line', { x1: O + k * P, y1: O, x2: O + k * P, y2: O + SIZE * P, class: 'lp-grid' }, tilt);
    }
    const nodes = [];
    for (let r = 0; r <= SIZE; r++) {
      for (let c = 0; c <= SIZE; c++) {
        const cx = O + c * P, cy = O + r * P;
        const g = el('g', { class: 'lp-node' }, tilt);
        el('circle', { cx, cy, r: 31 }, g);
        const t = el('text', { x: cx, y: cy + 8, 'text-anchor': 'middle' }, g);
        const value = binom(r + c, r);
        t.textContent = value;
        if (value >= 100) t.classList.add('small');
        nodes.push({ g, r, c, value });
      }
    }

    // ---- layer 3: Problem 15's 20 × 20 grid, shaded by how many routes reach each corner
    const big = el('g', { class: 'lp-layer lp-big' }, svg);
    const BP = 30, BO = (VIEW - BIG * BP) / 2;
    const maxLog = Math.log10(binom(2 * BIG, BIG));
    for (let r = 0; r <= BIG; r++) {
      for (let c = 0; c <= BIG; c++) {
        const shade = Math.log10(binom(r + c, r)) / maxLog;
        const dot = el('circle', { cx: BO + c * BP, cy: BO + r * BP, r: 4 + shade * 7, class: 'lp-dot' }, big);
        dot.style.opacity = String(0.18 + 0.82 * shade);
        dot.style.setProperty('--d', `${(r + c) * 45}ms`);
      }
    }
    el('circle', { cx: BO + BIG * BP, cy: BO + BIG * BP, r: 20, class: 'lp-goal' }, big);

    const CAPTIONS = [
      ['How many routes cross a grid?',
        'Start at the top-left corner and finish at the bottom-right, moving only right or down. '
        + 'A 2 × 2 grid has six routes.'],
      ['Listing them gets out of hand.',
        'Each step up in size multiplies the routes. Problem 15 asks about a 20 × 20 grid.'],
      ['Count at each corner instead.',
        'There is only one way to reach a corner on the top or left edge: straight along it.'],
      ['Add the two corners you came from.',
        'Every other corner is reached from just above it or just left of it, so its count is those two added.'],
      ['Tilt it: Pascal’s triangle.',
        'Each number is the sum of the two above it. People have drawn this triangle for a thousand years.'],
      ['Twenty by twenty: 400 additions.',
        'Over a hundred billion routes, counted without walking a single one.'],
    ];

    function show(s, animate) {
      step = s;
      const moving = animate && !reduceMotion;
      if (moving) {                       // drop the animation classes so a replay restarts them
        routes.classList.remove('play');
        big.classList.remove('play');
        for (const n of nodes) n.g.classList.remove('fresh');
        void box.getBoundingClientRect();
      }
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      table.hidden = s !== 1;
      routes.classList.toggle('on', s <= 1);
      routes.classList.toggle('play', moving && s === 0);
      counted.classList.toggle('on', s >= 2 && s <= 4);
      big.classList.toggle('on', s === 5);
      big.classList.toggle('play', moving && s === 5);
      counted.classList.toggle('tilted', s === 4);
      counted.classList.toggle('no-motion', !moving);
      for (const n of nodes) {
        const edge = n.r === 0 || n.c === 0;
        const shown = s >= 3 || (s === 2 && edge);
        const cls = ['lp-node'];
        if (shown) cls.push('shown');
        if (moving && ((s === 2 && edge) || (s === 3 && !edge))) {
          cls.push('fresh');
          n.g.style.setProperty('--d', `${(s === 2 ? n.r + n.c : n.r + n.c - 2) * 140}ms`);
        }
        if (s === 3 && n.r === 2 && n.c === 2) cls.push('focus');
        if (s === 3 && ((n.r === 1 && n.c === 2) || (n.r === 2 && n.c === 1))) cls.push('source');
        n.g.setAttribute('class', cls.join(' '));
      }
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
  window.DECK_PARTS.lattice = controller;
})();
