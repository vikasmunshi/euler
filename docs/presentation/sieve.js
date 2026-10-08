/* The sieve mini-story (Problems 7 and 10): cross out multiples on a 1–100 grid, one prime
   per step, then race the sieve against trial division below two million, live.
   Registers itself on window.DECK_PARTS; deck.js wires it to the slide data-viz="sieve". */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const N = 100, COLS = 10, PITCH = 70, CELL = 62;
  const PRIMES = [2, 3, 5, 7];          // every prime up to √100
  const RACE_LIMIT = 2_000_000;         // Problem 10's bound

  const el = (name, attrs = {}, parent = null) => {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  };
  const fmt = n => n.toLocaleString('en-GB');
  const secs = ms => (ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(2)} s`);
  const frame = () => new Promise(resolve => requestAnimationFrame(() => resolve()));

  /* Which step crosses out each number: the first prime p with p² ≤ n and p | n. */
  const crossedAt = new Map();
  PRIMES.forEach((p, i) => {
    for (let m = p * p; m <= N; m += p) if (!crossedAt.has(m)) crossedAt.set(m, i + 1);
  });

  function controller(slide) {
    const gridBox = slide.querySelector('[data-role="grid"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const tallyEl = slide.querySelector('[data-role="tally"]');
    const race = slide.querySelector('[data-role="race"]');
    const last = PRIMES.length + 2;     // 0 intro · 1–4 primes · 5 survivors · 6 race
    let step = 0, token = 0;

    // ---- the grid, built once
    const svg = el('svg', { viewBox: `0 0 ${COLS * PITCH} ${(N / COLS) * PITCH}`, role: 'img',
      'aria-label': 'The numbers 1 to 100' }, gridBox);
    const cells = new Map();
    for (let n = 1; n <= N; n++) {
      const i = n - 1, x = (i % COLS) * PITCH, y = Math.floor(i / COLS) * PITCH;
      const g = el('g', { class: 'sv' }, svg);
      el('rect', { x, y, width: CELL, height: CELL, rx: 6 }, g);
      const t = el('text', { x: x + CELL / 2, y: y + CELL / 2 + 9, 'text-anchor': 'middle' }, g);
      t.textContent = n;
      el('line', { x1: x + 12, y1: y + CELL - 12, x2: x + CELL - 12, y2: y + 12, pathLength: 1 }, g);
      cells.set(n, g);
    }

    /* Draw the grid as it stands after *s* steps; animate only what step s itself adds. */
    function paint(s, animate) {
      const passes = Math.min(s, PRIMES.length);
      let delay = 0;
      if (animate) {                      // drop the animation classes so a replay restarts them
        for (const g of cells.values()) g.classList.remove('fresh');
        void gridBox.getBoundingClientRect();
      }
      for (const [n, g] of cells) {
        const at = crossedAt.get(n);
        const isPrime = n > 1 && !at;
        const classes = ['sv'];
        if (n === 1) classes.push('one');
        if (at && at <= passes) {
          classes.push('crossed');
          if (animate && at === s) {
            g.style.setProperty('--d', `${delay}ms`);
            delay += 22;
            classes.push('fresh');
          }
        }
        const done = PRIMES.indexOf(n);
        if ((done >= 0 && done < passes) || (s > PRIMES.length && isPrime)) classes.push('prime');
        if (s >= 1 && s <= PRIMES.length && n === PRIMES[s - 1]) classes.push('current');
        g.setAttribute('class', classes.join(' '));
      }
      const gone = [...crossedAt.values()].filter(at => at <= passes).length;
      tallyEl.textContent = s === 0 ? '' : `${gone} crossed out, 0 divisions`;
    }

    function caption(s) {
      if (s === 0) {
        stepEl.textContent = 'Which numbers up to 100 are prime?';
        detailEl.textContent = 'A prime can only be divided evenly by 1 and itself. 1 doesn’t count.';
      } else if (s <= PRIMES.length) {
        const p = PRIMES[s - 1];
        stepEl.textContent = `${p} is prime.`;
        detailEl.textContent = s === 1
          ? `Cross out every multiple of ${p} after it: 4, 6, 8 and so on.`
          : `Cross out its multiples, starting at ${p} × ${p} = ${p * p}. `
            + 'The smaller ones were already crossed out by an earlier prime.';
      } else if (s === PRIMES.length + 1) {
        stepEl.textContent = 'Everything left is prime.';
        detailEl.textContent = 'All 25 of them. We could stop at 7, because 11 × 11 = 121 is already past 100.';
      } else {
        stepEl.textContent = 'Now every prime below two million.';
        detailEl.textContent = 'That’s Problem 10. Both methods are running right now, in this browser.';
      }
    }

    function show(s, animate) {
      step = s;
      token++;
      caption(s);
      paint(Math.min(s, PRIMES.length + 1), animate && !reduceMotion);
      slide.classList.toggle('racing', s === last);
      race.hidden = s !== last;
      if (s === last) runRace(token);
    }

    // ---- the race
    async function runRace(my) {
      const rows = {
        sieve: race.querySelector('[data-race="sieve"]'),
        trial: race.querySelector('[data-race="trial"]'),
      };
      const verdict = race.querySelector('[data-role="verdict"]');
      for (const row of Object.values(rows)) {
        row.querySelector('.bar i').style.width = '0%';
        row.querySelector('.time').textContent = '';
        row.querySelector('.ops').textContent = '';
      }
      verdict.textContent = '';
      await frame();
      if (my !== token) return;

      // the sieve: one pass, fast enough to run in a single frame
      let t = performance.now();
      const composite = new Uint8Array(RACE_LIMIT);
      let marks = 0;
      for (let p = 2; p * p < RACE_LIMIT; p++) {
        if (composite[p]) continue;
        for (let m = p * p; m < RACE_LIMIT; m += p) { composite[m] = 1; marks++; }
      }
      let primes = 0;
      for (let n = 2; n < RACE_LIMIT; n++) if (!composite[n]) primes++;
      const sieveMs = performance.now() - t;
      rows.sieve.querySelector('.time').textContent = secs(sieveMs);
      rows.sieve.querySelector('.ops').textContent = `${fmt(marks)} cross-outs`;
      rows.sieve.querySelector('.bar i').style.width = '100%';

      // trial division: divide by every number up to √n, in slices so the timer can tick.
      // Only the slices are timed, not the frames between them.
      let trialMs = 0, divisions = 0, n = 2, found = 0;
      while (n < RACE_LIMIT) {
        t = performance.now();
        const sliceEnd = Math.min(n + 40_000, RACE_LIMIT);
        for (; n < sliceEnd; n++) {
          const r = Math.floor(Math.sqrt(n));
          let d = 2;
          for (; d <= r; d++) { divisions++; if (n % d === 0) break; }
          if (d > r) found++;
        }
        trialMs += performance.now() - t;
        rows.trial.querySelector('.time').textContent = secs(trialMs);
        rows.trial.querySelector('.ops').textContent = `${fmt(divisions)} divisions`;
        rows.trial.querySelector('.bar i').style.width = `${(n / RACE_LIMIT) * 100}%`;
        await frame();
        if (my !== token) return;
      }
      verdict.textContent = found === primes
        ? `Both found ${fmt(primes)} primes. The sieve did ${Math.round(divisions / marks)}× less work `
          + `and finished ${Math.round(trialMs / sieveMs)}× sooner.`
        : 'The two methods disagree: check the code.';
    }

    return {
      enter(direction) { show(direction < 0 ? last - 1 : 0, false); },
      leave() { token++; },
      next() { if (step >= last) return false; show(step + 1, true); return true; },
      prev() { if (step <= 0) return false; show(step - 1, false); return true; },
      replay() { show(step, true); },
      jump(s) { show(Math.max(0, Math.min(last, s)), false); },
    };
  }

  window.DECK_PARTS = window.DECK_PARTS || {};
  window.DECK_PARTS.sieve = controller;
})();
