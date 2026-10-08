/* The big-numbers mini-story (Problem 16): double 2 a thousand times, watch a calculator give
   up, see all 302 digits, learn how a computer keeps them (school long multiplication), and
   compare with the atoms in the universe. Problem 16's own answer — the sum of the digits —
   is never shown. Registers itself on window.DECK_PARTS (data-viz="bignum"). */
(() => {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const POWER = 1000;
  const ATOM_DIGITS = 81;                     // about 10⁸⁰ atoms in the observable universe
  const pow2 = k => (2n ** BigInt(k)).toString();
  const DIGITS = pow2(POWER);
  const fmt = n => n.toLocaleString('en-GB');

  const h = (tag, cls, parent, content) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (content !== undefined) node.textContent = content;
    if (parent) parent.appendChild(node);
    return node;
  };

  /* 32,768 × 2, column by column from the right: [digit written, carry into the next column]. */
  const SUM_TOP = '32768';
  const columns = [];
  {
    let carry = 0;
    for (let i = SUM_TOP.length - 1; i >= 0; i--) {
      const v = Number(SUM_TOP[i]) * 2 + carry;
      columns.unshift({ top: SUM_TOP[i], out: String(v % 10), carryIn: carry, carryOut: Math.floor(v / 10) });
      carry = Math.floor(v / 10);
    }
    if (carry) columns.unshift({ top: '', out: String(carry), carryIn: carry, carryOut: 0 });
  }

  function controller(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const tallyEl = slide.querySelector('[data-role="tally"]');
    const stage = h('div', 'bn-stage', box);
    const layers = [];
    const layer = name => { const d = h('div', `bn-layer bn-${name}`, stage); layers.push(d); return d; };
    const last = 4;
    let step = 0, token = 0;

    // ---- 0: the first ten doublings
    const ladder = layer('ladder');
    for (let k = 1; k <= 10; k++) {
      const row = h('div', 'bn-rung', ladder);
      row.style.setProperty('--d', `${k * 110}ms`);
      h('span', 'bn-exp', row).innerHTML = `2<sup>${k}</sup>`;
      h('span', 'bn-val', row, fmt(Number(pow2(k))));
    }

    // ---- 1: what a calculator shows
    const calc = layer('calc');
    const display = h('div', 'bn-display', calc);
    h('span', 'bn-mantissa', display, `${DIGITS[0]}.${DIGITS.slice(1, 10)}`);
    h('span', 'bn-power', display).innerHTML = `× 10<sup>${DIGITS.length - 1}</sup>`;
    h('p', 'bn-lost', calc, `Ten digits kept. The other ${DIGITS.length - 10} are gone.`);

    // ---- 2 & 4: the digits themselves
    const grid = layer('digits');
    const cells = [];
    for (let i = 0; i < DIGITS.length; i++) cells.push(h('span', 'bn-d', grid, ''));
    const fill = digits => cells.forEach((c, i) => { c.textContent = digits[i] || ''; });

    async function doubleUp(my) {
      const start = performance.now(), length = 3600;
      for (;;) {
        const t = Math.min(1, (performance.now() - start) / length);
        const k = Math.max(1, Math.round(POWER * t * t));     // ease in: slow start, fast finish
        const digits = pow2(k);
        fill(digits);
        tallyEl.textContent = `2 to the power ${fmt(k)}: ${fmt(digits.length)} digit${digits.length === 1 ? '' : 's'}`;
        if (t >= 1) return;
        await new Promise(resolve => requestAnimationFrame(resolve));
        if (my !== token) return;
      }
    }

    // ---- 3: doubling the way you learned at school
    const sum = layer('sum');
    const table = h('div', 'bn-sum-table', sum);
    table.style.setProperty('--cols', columns.length + 1);
    const row = cls => h('div', `bn-sum-row ${cls}`, table);
    const carries = row('carries'), top = row('top'), times = row('times'), result = row('result');
    h('span', '', carries); h('span', '', top); h('span', 'op', times, '×'); h('span', '', result);
    const carryCells = [], outCells = [];
    columns.forEach((col, i) => {
      carryCells.push(h('span', 'carry', carries, col.carryIn ? String(col.carryIn) : ''));
      h('span', '', top, col.top);
      h('span', '', times, i === columns.length - 1 ? '2' : '');
      outCells.push(h('span', 'out', result, col.out));
    });
    const revealSum = animate => {
      const n = columns.length;
      columns.forEach((_, i) => {
        const order = n - 1 - i;            // right to left
        for (const c of [outCells[i], carryCells[i]]) {
          c.style.setProperty('--d', `${order * 520}ms`);
          c.classList.toggle('play', animate);
        }
      });
    };

    const CAPTIONS = [
      ['Double it, and keep doubling.', 'Ten doublings of 2 already make 1,024. Problem 16 asks about a thousand.'],
      ['A calculator gives up.', 'It keeps the first few digits and an exponent. Everything after the tenth digit is thrown away.'],
      [`All ${DIGITS.length} digits.`, 'A computer can keep every one of them. Here they are, doubling all the way up to 2 to the power 1,000.'],
      ['The same way you learned at school.',
        'Double each digit from the right and carry the tens, just like long multiplication on paper. A thousand times over.'],
      ['More than every atom in the universe.', `There are about 10⁸⁰ atoms in the observable universe, a number ${ATOM_DIGITS} digits long. `
        + `2 to the power 1,000 is ${DIGITS.length} digits long.`],
    ];

    function show(s, animate) {
      step = s;
      const my = ++token;
      const moving = animate && !reduceMotion;
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      tallyEl.textContent = '';
      for (const l of layers) l.classList.remove('on', 'play');
      void box.getBoundingClientRect();     // restart animations on replay
      const visible = [ladder, calc, grid, sum, grid][s];
      visible.classList.add('on');
      if (moving) visible.classList.add('play');
      grid.classList.toggle('atoms', s === 4);
      cells.forEach((c, i) => c.classList.toggle('atom', s === 4 && i < ATOM_DIGITS));
      if (s === 2 && moving) doubleUp(my);
      else fill(DIGITS);
      if (s === 2 && !moving) tallyEl.textContent = `2 to the power 1,000: ${DIGITS.length} digits`;
      if (s === 3) { revealSum(false); void box.getBoundingClientRect(); revealSum(moving); }
      if (s === 4) tallyEl.textContent = `Highlighted: how long the count of atoms would be (${ATOM_DIGITS} digits).`;
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
  window.DECK_PARTS.bignum = controller;
})();
