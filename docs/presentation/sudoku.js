/* The Su Doku mini-story (Problem 96), in two slides. The first counts: every blank any digit,
   then whole boards under the box, row and column rules, down to the 6.67 × 10²¹ valid grids,
   too many to list and look up. The second searches: pencil in the candidates of the statement's
   own example grid, let one placement force the next until it is solved, then compare the
   three kept solvers. Problem 96's answer (the sum over all fifty grids) is never shown; Grid 01
   and its 483 are printed in the problem statement. Registers itself on window.DECK_PARTS
   (data-viz="sudoku-count" and data-viz="sudoku-search"). */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const fmt = n => n.toLocaleString('en-GB');

  /* Grid 01 of the puzzle file: the example in the problem statement. 0 is a blank. */
  const PUZZLE = [...'003020600900305001001806400008102900700000008006708200002609500800203009005010300'].map(Number);
  const BLANKS = PUZZLE.filter(d => !d).length;

  const el = (name, attrs = {}, parent = null) => {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  };
  const h = (tag, cls, parent, content) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (content !== undefined) node.textContent = content;
    if (parent) parent.appendChild(node);
    return node;
  };

  // ---------------------------------------------------------------- the rules

  const UNITS = [];
  for (let r = 0; r < 9; r++) UNITS.push([...Array(9)].map((_, c) => r * 9 + c));
  for (let c = 0; c < 9; c++) UNITS.push([...Array(9)].map((_, r) => r * 9 + c));
  for (let b = 0; b < 9; b++) {
    const r0 = Math.floor(b / 3) * 3, c0 = (b % 3) * 3;
    UNITS.push([...Array(9)].map((_, k) => (r0 + Math.floor(k / 3)) * 9 + c0 + (k % 3)));
  }
  const PEERS = [...Array(81)].map((_, x) => {
    const set = new Set();
    for (const u of UNITS) if (u.includes(x)) u.forEach(y => set.add(y));
    set.delete(x);
    return [...set];
  });
  const candidates = (grid, x) => {
    const taken = new Set(PEERS[x].map(p => grid[p]));
    return [1, 2, 3, 4, 5, 6, 7, 8, 9].filter(d => !taken.has(d));
  };

  /* Solve by deduction alone, a wave at a time: every blank with one candidate left, and every
     digit with one place left in a row, column or box, is placed together from the same board.
     Returns [{cell, digit}] per wave; Grid 01 needs four waves and no guess. */
  function waves(start) {
    const grid = start.slice(), out = [];
    while (grid.includes(0)) {
      const place = new Map();
      for (let x = 0; x < 81; x++) {
        if (grid[x]) continue;
        const c = candidates(grid, x);
        if (c.length === 1) place.set(x, c[0]);
      }
      for (const u of UNITS) {
        for (let d = 1; d <= 9; d++) {
          if (u.some(y => grid[y] === d)) continue;
          const spots = u.filter(y => !grid[y] && candidates(grid, y).includes(d));
          if (spots.length === 1 && !place.has(spots[0])) place.set(spots[0], d);
        }
      }
      if (!place.size) break;                 // stuck: the slide would need a guess here
      for (const [x, d] of place) grid[x] = d;
      out.push([...place].map(([cell, digit]) => ({ cell, digit })));
    }
    return out;
  }

  // ---------------------------------------------------------------- the board

  const PITCH = 64, PAD = 8, SIZE = 9 * PITCH + 2 * PAD;

  /* A 9×9 board in an SVG: each cell has a large digit and nine pencil marks. */
  function board(container) {
    const svg = el('svg', { viewBox: `0 0 ${SIZE} ${SIZE}`, role: 'img', class: 'sd-board' }, container);
    svg.setAttribute('aria-label', 'A Su Doku grid');
    const cells = [];
    for (let x = 0; x < 81; x++) {
      const r = Math.floor(x / 9), c = x % 9, x0 = PAD + c * PITCH, y0 = PAD + r * PITCH;
      const g = el('g', { class: 'sd-cell' }, svg);
      el('rect', { x: x0, y: y0, width: PITCH, height: PITCH }, g);
      const big = el('text', { x: x0 + PITCH / 2, y: y0 + PITCH / 2 + 13, 'text-anchor': 'middle', class: 'sd-digit' }, g);
      const marks = [];
      for (let d = 1; d <= 9; d++) {
        const mx = x0 + 13 + ((d - 1) % 3) * 19, my = y0 + 18 + Math.floor((d - 1) / 3) * 19;
        const t = el('text', { x: mx, y: my, 'text-anchor': 'middle', class: 'sd-mark' }, g);
        t.textContent = String(d);
        marks.push(t);
      }
      cells.push({ g, big, marks });
    }
    for (let k = 0; k <= 9; k++) {
      const p = PAD + k * PITCH, cls = k % 3 ? 'sd-thin' : 'sd-thick';
      el('line', { x1: PAD, y1: p, x2: SIZE - PAD, y2: p, class: cls }, svg);
      el('line', { x1: p, y1: PAD, x2: p, y2: SIZE - PAD, class: cls }, svg);
    }
    /* Draw a whole board: digits[x] (0 blank), per-cell class, and the pencil marks to show. */
    const draw = (digits, cls = () => '', marks = () => []) => cells.forEach((cell, x) => {
      cell.big.textContent = digits[x] ? String(digits[x]) : '';
      cell.g.setAttribute('class', `sd-cell ${PUZZLE[x] ? 'given' : ''} ${cls(x)}`.trim());
      const shown = new Set(digits[x] ? [] : marks(x));
      cell.marks.forEach((m, i) => m.classList.toggle('on', shown.has(i + 1)));
    });
    return { svg, cells, draw };
  }

  // ---------------------------------------------------------------- slide 1: counting

  const FACT9 = 362880n;
  const BAND = FACT9 * 56n * 6n ** 6n;        // one band of three boxes, rows and boxes ruled
  const VALID = 6670903752021072936960n;      // Felgenhauer and Jarvis, 2005
  const RUNGS = [
    ['Any digit in any cell', 9n ** 81n],
    ['Each 3 × 3 box holds 1 to 9', FACT9 ** 9n],
    ['… and each row', BAND ** 3n],
    ['… and each column: every valid Su Doku', VALID],
  ];
  const SUP = { 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
  const sup = n => [...String(n)].map(c => SUP[c]).join('');
  const sci = big => {                        // two significant figures, rounded
    const s = big.toString(), m = Math.round(Number(s.slice(0, 3)) / 10);
    const [mant, exp] = m === 100 ? ['1.0', s.length] : [`${String(m)[0]}.${String(m)[1]}`, s.length - 1];
    return `${mant} × 10${sup(exp)}`;
  };

  function counting(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const tallyEl = slide.querySelector('[data-role="tally"]');
    const stage = h('div', 'sd-stage', box);
    const boardLayer = h('div', 'sd-layer', stage);
    const { draw } = board(boardLayer);
    const ladder = h('div', 'sd-layer sd-ladder', stage);
    const rungs = RUNGS.map(([rule, n]) => {
      const row = h('div', 'sd-rung', ladder);
      h('span', 'sd-rule', row, rule);
      h('span', 'sd-num', row, n.toString());
      h('span', 'sd-sci', row, `${sci(n)} · ${n.toString().length} digits`);
      return row;
    });
    const blind = 9n ** BigInt(BLANKS);
    let seed = 96;                            // one fixed blind filling, for a jump or reduced motion
    const FROZEN = PUZZLE.map(d => d || 1 + ((seed = (seed * 48271) % 2147483647) % 9));
    const last = 6;
    let step = 0, token = 0;

    async function flicker(my) {
      for (;;) {
        draw(PUZZLE.map(d => d || 1 + Math.floor(Math.random() * 9)), x => (PUZZLE[x] ? '' : 'guessed'));
        await sleep(90);
        if (my !== token) return;
      }
    }

    const CAPTIONS = [
      ['81 cells, 32 given.', `Every row, column and 3 × 3 box must hold the digits 1 to 9 once each. This is Grid 01, the example in Problem 96: ${BLANKS} blanks to fill.`],
      ['Try every digit in every blank?', `${BLANKS} blanks with 9 choices each make 9${sup(BLANKS)} boards. At a billion a second, checking them all would take about 10³⁰ years; the universe is 1.4 × 10¹⁰ years old.`],
      ['Most of those boards are nonsense.', 'A 9 in every blank is one of them. Blind counting spends nearly all its time on boards that break a rule in the very first row.'],
      ['Count only boards that keep a rule.', 'Forget the clues and count whole boards. Each 3 × 3 box is a shuffle of 1 to 9, 9! = 362,880 ways, and there are nine boxes.'],
      ['Add the rows.', 'Rows and boxes split the board into three bands of three boxes. Each band can be filled 948,109,639,680 ways, independently of the others.'],
      ['Add the columns.', 'What survives is every finished Su Doku there is: 6,670,903,752,021,072,936,960, counted in 2005 by Bertram Felgenhauer and Frazer Jarvis.'],
      ['List them once, then look up?', 'At a billion grids a second, listing them takes 211,000 years. At 81 bytes a grid, storing them takes 540 zettabytes. So every solver searches instead.'],
    ];

    function show(s, animate) {
      step = s;
      const my = ++token;
      const moving = animate && !reduceMotion;
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      tallyEl.textContent = '';
      boardLayer.classList.toggle('on', s <= 2);
      ladder.classList.toggle('on', s >= 3);
      rungs.forEach((row, i) => {
        row.classList.toggle('on', s >= 3 && i <= Math.min(s - 2, 3));
        row.classList.toggle('final', s === 6 && i === 3);
      });
      if (s === 0) draw(PUZZLE);
      if (s === 1) {
        tallyEl.textContent = `9${sup(BLANKS)} = ${fmt(blind)} boards`;
        if (moving) flicker(my);
        else draw(FROZEN, x => (PUZZLE[x] ? '' : 'guessed'));
      }
      if (s === 2) draw(PUZZLE.map(d => d || 9), x => (PUZZLE[x] ? '' : 'wrong'));
      if (s >= 3) tallyEl.textContent = 'Each number is written out in full: its length is its size.';
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

  // ---------------------------------------------------------------- slide 2: searching

  function searching(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const tallyEl = slide.querySelector('[data-role="tally"]');
    const compare = slide.querySelector('[data-role="compare"]');
    const methods = slide.querySelector('[data-role="methods"]');
    const stage = h('div', 'sd-stage', box);
    const layer = h('div', 'sd-layer on', stage);
    const { draw } = board(layer);
    const plan = waves(PUZZLE);
    const solved = PUZZLE.slice();
    for (const wave of plan) for (const { cell, digit } of wave) solved[cell] = digit;
    const pencil = grid => x => candidates(grid, x);
    const marks = PUZZLE.reduce((n, d, x) => n + (d ? 0 : candidates(PUZZLE, x).length), 0);
    const placed = x => (PUZZLE[x] ? '' : 'placed');
    const last = 3;
    let step = 0, token = 0;

    async function cascade(my) {
      const grid = PUZZLE.slice();
      draw(grid, () => '', pencil(grid));
      for (let w = 0; w < plan.length; w++) {
        await sleep(w ? 1500 : 700);
        if (my !== token) return;
        const fresh = new Set(plan[w].map(p => p.cell));
        for (const { cell, digit } of plan[w]) grid[cell] = digit;
        draw(grid, x => (fresh.has(x) ? 'placed fresh' : PUZZLE[x] || !grid[x] ? '' : 'placed'), pencil(grid));
        tallyEl.textContent = `Wave ${w + 1}: ${plan[w].length} cells placed`;
      }
      await sleep(1500);
      if (my !== token) return;
      tallyEl.textContent = `Solved in ${plan.length} waves, without a single guess.`;
    }

    const CAPTIONS = [
      ['Pencil in what each blank could be.', 'Start every blank with 1 to 9 and cross out each digit already in its row, column or box.'],
      ['One placement forces the next.', 'A blank left with one candidate is decided; so is a digit with only one place left in a row, column or box. Each placement crosses out more.'],
      ['Guess only when stuck.', 'Forty of the fifty puzzles fall to deduction alone. For the rest, guess in the blank with the fewest candidates, deduce again, and back up on a contradiction.'],
      ['Three solvers, a few milliseconds each.', 'All fifty puzzles, as kept for Problem 96. The general puzzle is NP-complete: no shortcut is known, only better ways to search.'],
    ];

    function show(s, animate) {
      step = s;
      const my = ++token;
      const moving = animate && !reduceMotion;
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      tallyEl.textContent = '';
      compare.hidden = s !== 2;
      methods.hidden = s !== 3;
      if (s === 0) {
        draw(PUZZLE, () => '', pencil(PUZZLE));
        tallyEl.textContent = `${BLANKS} blanks, ${marks} candidates pencilled in`;
      }
      if (s === 1) {
        if (moving) cascade(my);
        else { draw(solved, placed); tallyEl.textContent = `Solved in ${plan.length} waves, without a single guess.`; }
      }
      if (s === 2) draw(solved, placed);
      if (s === 3) draw(solved, x => `${placed(x)} ${x < 3 ? 'corner' : ''}`);
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
  window.DECK_PARTS['sudoku-count'] = counting;
  window.DECK_PARTS['sudoku-search'] = searching;
})();
