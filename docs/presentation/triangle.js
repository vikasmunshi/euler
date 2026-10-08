/* The maximum-path-sum mini-story (Problems 18 and 67): try every path through the small
   triangle from Problem 18's statement, see why that cannot scale to Problem 67's 100 rows,
   then fold the triangle from the bottom up. Neither problem's own answer is shown: the
   worked example is the statement's (best total 23), and the 100-row triangle is drawn as dots.
   Registers itself on window.DECK_PARTS; deck.js wires it to the slide data-viz="triangle". */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const VIEW = 700;
  const ROWS = [[3], [7, 4], [2, 4, 6], [8, 5, 9, 3]];   // Problem 18's worked example
  const DEPTH = ROWS.length - 1;
  const BIG_ROWS = 100;                                   // Problem 67

  const el = (name, attrs = {}, parent = null) => {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  };
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

  // best[r][c]: the best total from (r, c) to the bottom; pick[r][c]: which child it takes
  const best = ROWS.map(row => [...row]);
  const pick = ROWS.map(row => row.map(() => 0));
  for (let r = DEPTH - 1; r >= 0; r--) {
    for (let c = 0; c <= r; c++) {
      const left = best[r + 1][c], right = best[r + 1][c + 1];
      pick[r][c] = right > left ? c + 1 : c;
      best[r][c] = ROWS[r][c] + Math.max(left, right);
    }
  }
  const bestPath = [0];
  for (let r = 0; r < DEPTH; r++) bestPath.push(pick[r][bestPath[r]]);

  function controller(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const tallyEl = slide.querySelector('[data-role="tally"]');
    const svg = el('svg', { viewBox: `0 0 ${VIEW} ${VIEW}`, role: 'img' }, box);
    const last = 6;
    let step = 0, token = 0;

    // ---- the small triangle
    const small = el('g', { class: 'tr-layer tr-small' }, svg);
    const DX = 150, DY = 150, TOP = 130;
    const pos = (r, c) => [VIEW / 2 + (c - r / 2) * DX, TOP + r * DY];
    const edges = el('g', {}, small);
    const edgeAt = new Map();
    for (let r = 0; r < DEPTH; r++) {
      for (let c = 0; c <= r; c++) {
        for (const child of [c, c + 1]) {
          const [x1, y1] = pos(r, c), [x2, y2] = pos(r + 1, child);
          edgeAt.set(`${r},${c},${child}`, el('line', { x1, y1, x2, y2, class: 'tr-edge' }, edges));
        }
      }
    }
    const trail = el('polyline', { class: 'tr-trail', points: '' }, small);
    const nodes = ROWS.map((row, r) => row.map((value, c) => {
      const [cx, cy] = pos(r, c);
      const g = el('g', { class: 'tr-node' }, small);
      el('circle', { cx, cy, r: 46 }, g);
      const t = el('text', { x: cx, y: cy + 12, 'text-anchor': 'middle', class: 'tr-value' }, g);
      return { g, t, value };
    }));

    // ---- Problem 67's 100 rows, as dots
    const big = el('g', { class: 'tr-layer tr-big' }, svg);
    const BS = 6.4, BT = 40;
    const bigRows = [];
    for (let r = 0; r < BIG_ROWS; r++) {
      const row = el('g', { class: 'tr-dots' }, big);
      row.style.setProperty('--d', `${(BIG_ROWS - 1 - r) * 22}ms`);
      for (let c = 0; c <= r; c++) {
        el('circle', { cx: VIEW / 2 + (c - r / 2) * BS, cy: BT + r * BS, r: 2.3 }, row);
      }
      bigRows.push(row);
    }

    const pathPoints = cols => cols.map((c, r) => pos(r, c).join(',')).join(' ');
    const pathSum = cols => cols.reduce((sum, c, r) => sum + ROWS[r][c], 0);
    const allPaths = [];
    for (let bits = 0; bits < 2 ** DEPTH; bits++) {
      const cols = [0];
      for (let r = 0; r < DEPTH; r++) cols.push(cols[r] + ((bits >> (DEPTH - 1 - r)) & 1));
      allPaths.push(cols);
    }

    /* Rows folded so far: step 3 folds the row above the bottom, step 5 reaches the top. */
    const foldedFrom = s => (s >= 3 && s <= 5 ? DEPTH - (s - 2) : DEPTH + 1);

    function paintSmall(s) {
      const from = foldedFrom(s), newest = from;
      for (let r = 0; r <= DEPTH; r++) {
        for (let c = 0; c <= r; c++) {
          const n = nodes[r][c], folded = r >= from && r < DEPTH;
          const cls = ['tr-node'];
          if (folded) cls.push('folded');
          if (r > from && from <= DEPTH && !(s === 5 && bestPath[r] === c)) cls.push('spent');
          if (s === 5 && r === 0) cls.push('answer');
          n.g.setAttribute('class', cls.join(' '));
          n.t.textContent = folded ? best[r][c] : n.value;
        }
      }
      for (const [key, line] of edgeAt) {
        const [r, c, child] = key.split(',').map(Number);
        const chosen = r === newest && s >= 3 && s <= 4 && pick[r][c] === child;
        line.setAttribute('class', `tr-edge${chosen ? ' chosen' : ''}${r > from ? ' spent' : ''}`);
      }
      trail.setAttribute('points', s === 5 ? pathPoints(bestPath) : '');
      trail.setAttribute('class', `tr-trail${s === 5 ? ' best' : ''}`);
    }

    async function tryEveryPath(my, animate) {
      let top = null;
      for (let i = 0; i < allPaths.length; i++) {
        const cols = allPaths[i], total = pathSum(cols);
        if (!top || total > pathSum(top)) top = cols;
        if (animate) {
          trail.setAttribute('points', pathPoints(cols));
          trail.setAttribute('class', 'tr-trail');
          tallyEl.textContent = `Path ${i + 1} of ${allPaths.length}: `
            + `${cols.map((c, r) => ROWS[r][c]).join(' + ')} = ${total}`;
          await sleep(650);
          if (my !== token) return;
        }
      }
      trail.setAttribute('points', pathPoints(top));
      trail.setAttribute('class', 'tr-trail best');
      tallyEl.textContent = `Best of ${allPaths.length} paths: ${pathSum(top)}`;
    }

    function caption(s) {
      const say = (step, detail) => { stepEl.textContent = step; detailEl.textContent = detail; };
      const picks = r => ROWS[r].map((v, c) => `${v} picks ${best[r + 1][pick[r][c]]}`).join(', ');
      switch (s) {
        case 0: return say('Find the biggest total, top to bottom.',
          'Start at the top and step down to one of the two numbers just below, row by row. '
          + 'This small one is the example from Problem 18.');
        case 1: return say('Try every path.', `Four rows give ${allPaths.length} paths. Add each one up and keep the best.`);
        case 2: return say('Problem 67 has 100 rows.',
          'That’s 2⁹⁹ paths, about 6 × 10²⁹. At a trillion paths a second, checking them all would '
          + 'take 20 billion years: longer than the universe has existed.');
        case 3: return say('Start from the bottom instead.',
          `Each number in the third row only needs the better of the two below it: ${picks(DEPTH - 1)}.`);
        case 4: return say('Fold the next row up.', `Same again: ${picks(DEPTH - 2)}. The rows below are no longer needed.`);
        case 5: return say('The top holds the answer.',
          `${best[0][0]} is the best total, found with three rows of small additions instead of ${allPaths.length} paths.`);
        default: return say('A hundred rows, folded in a blink.',
          'About 5,000 additions instead of 6 × 10²⁹ paths. Same trick, any size.');
      }
    }

    function show(s, animate) {
      step = s;
      const my = ++token;
      const moving = animate && !reduceMotion;
      caption(s);
      tallyEl.textContent = '';
      const isBig = s === 2 || s === last;
      small.classList.toggle('on', !isBig);
      big.classList.toggle('on', isBig);
      big.classList.remove('folding', 'folded-all');
      if (s === last) {
        void box.getBoundingClientRect();     // restart the wave on replay
        big.classList.add(moving ? 'folding' : 'folded-all');
      }
      paintSmall(s);
      if (s === 1) tryEveryPath(my, moving);
      if (s >= 3 && s <= 4) {
        const r = foldedFrom(s);
        tallyEl.textContent = ROWS[r].map((v, c) => `${v} + ${best[r + 1][pick[r][c]]} = ${best[r][c]}`).join(',  ');
      }
      if (s === 5) tallyEl.textContent = `${ROWS[0][0]} + ${best[1][pick[0][0]]} = ${best[0][0]}.  `
        + `Best path: ${bestPath.map((c, r) => ROWS[r][c]).join(' → ')}`;
    }

    return {
      enter(direction) { show(direction < 0 ? last : 0, direction >= 0); },
      leave() { token++; },
      next() { if (step >= last) return false; show(step + 1, true); return true; },
      prev() { if (step <= 0) return false; show(step - 1, false); return true; },
      replay() { show(step, true); },
      jump(s) { show(Math.max(0, Math.min(last, s)), false); },
    };
  }

  window.DECK_PARTS = window.DECK_PARTS || {};
  window.DECK_PARTS.triangle = controller;
})();
