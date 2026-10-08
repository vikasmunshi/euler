/* The general-audience slides around the mini-stories: the opener (the obvious way breaks),
   the Project Euler intro, the long pause, what changed, the vault, working with AI, and the
   live-demo picker. Each registers a controller on window.DECK_PARTS, keyed by data-viz.
   Public material only: no answers, nothing from solutions/private/. */
(() => {
  'use strict';

  const SVG = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const HISTORY = window.HISTORY || { problems: [], project: {} };
  const problems = HISTORY.problems.map(([n, title, level, pct, solvers, solved, date]) => ({
    n, title, solvers: Number.isInteger(solvers) ? solvers : null, solved, date: date ? new Date(date) : null,
  }));
  const fmt = n => n.toLocaleString('en-GB');
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const frame = () => new Promise(resolve => requestAnimationFrame(() => resolve()));
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
  const fill = (slide, key, value) => slide.querySelectorAll(`[data-fill="${key}"]`)
    .forEach(node => { node.textContent = value; });

  /* A controller with steps 0..last, built from a show(step, animate) function. */
  function stepped(last, show, leave = () => {}) {
    let step = 0;
    const go = (s, animate) => { step = s; show(s, animate && !reduceMotion); };
    return {
      enter(direction) { go(direction < 0 ? last : 0, direction >= 0); },
      leave,
      next() { if (step >= last) return false; go(step + 1, true); return true; },
      prev() { if (step <= 0) return false; go(step - 1, false); return true; },
      replay() { go(step, true); },
      jump(s) { go(Math.max(0, Math.min(last, s)), false); },
    };
  }

  // ======================================================== the opener: the obvious way breaks

  /* Problem 1's question below `limit`, counted one number at a time. The sum is never shown. */
  const oneByOne = limit => { let s = 0; for (let i = 1; i < limit; i++) if (i % 3 === 0 || i % 5 === 0) s += i; return s; };
  /* The same sum in one step: k × (1 + 2 + … + m) for the multiples of k, minus the double-counted 15s. */
  const clever = limit => {
    const n = BigInt(limit) - 1n;
    const tri = k => { const m = n / k; return k * m * (m + 1n) / 2n; };
    return tri(3n) + tri(5n) - tri(15n);
  };
  const humanTime = seconds => {
    if (seconds < 1e-3) return 'under a millisecond';
    if (seconds < 1) return `${Math.round(seconds * 1000)} milliseconds`;
    if (seconds < 120) return `${seconds.toFixed(seconds < 10 ? 1 : 0)} seconds`;
    if (seconds < 7200) return `${Math.round(seconds / 60)} minutes`;
    if (seconds < 172800) return `${Math.round(seconds / 3600)} hours`;
    if (seconds < 3.2e7 * 2) return `${Math.round(seconds / 86400)} days`;
    return `${fmt(Math.round(seconds / 3.156e7))} years`;
  };

  function opener(slide) {
    const table = slide.querySelector('[data-role="rows"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const ROWS = [
      { limit: 1e3, label: '1,000', measure: true },
      { limit: 1e6, label: 'a million', measure: true },
      { limit: 1e8, label: 'a hundred million', measure: true },
      { limit: 1e12, label: 'a trillion' },
      { limit: 1e18, label: 'a billion billion' },
    ];
    let rate = null;                       // numbers checked per second, measured on this machine
    const rowEls = ROWS.map(r => {
      const tr = h('div', 'ob-row', table);
      h('span', 'ob-limit', tr, `Below ${r.label}`);
      const bar = h('span', 'ob-bar', tr); h('i', '', bar);
      h('span', 'ob-slow', tr);
      h('span', 'ob-fast', tr);
      return tr;
    });
    const timeRow = (r, tr) => {
      let seconds, note = '';
      if (r.measure) {
        const t = performance.now(); const slow = oneByOne(r.limit); const ms = performance.now() - t;
        seconds = ms / 1000;
        if (r.limit >= 1e6) rate = r.limit / Math.max(seconds, 1e-6);
        if (BigInt(slow) !== clever(r.limit)) note = ' (the two disagree!)';
      } else {
        seconds = r.limit / (rate || 3e8);
        note = ' (estimated)';
      }
      const t = performance.now(); clever(r.limit); const fastMs = performance.now() - t;
      tr.querySelector('.ob-slow').textContent = humanTime(seconds) + note;
      tr.querySelector('.ob-fast').textContent = humanTime(fastMs / 1000);
      // log scale: a microsecond is empty, a hundred thousand years is full
      const frac = Math.max(0.01, Math.min(1, (Math.log10(Math.max(seconds, 1e-6)) + 6) / (6 + 12.5)));
      tr.querySelector('.ob-bar i').style.width = `${frac * 100}%`;
    };
    const CAPTIONS = [
      ['Counting one by one is fine for Problem 1.', 'Check each number below 1,000, add up the multiples of 3 or 5. This laptop does it in a blink.'],
      ['Ask about a million.', 'Still fast. Every row on this slide is timed live, right now, on this laptop.'],
      ['A hundred million.', 'Now you can feel it. Same question, same method, a hundred times more numbers.'],
      ['A trillion.', 'Too long to wait for here, so this row is estimated from the measured speed.'],
      ['A billion billion.', 'Counting one by one would outlast us all. The clever column hasn’t moved.'],
      ['The clever way: one formula.', 'The multiples of 3 are 3 × (1 + 2 + … + n), and 1 + 2 + … + n is just n × (n + 1) ÷ 2, '
        + 'the shortcut a young Gauss is said to have found. Instant, at any size. That gap is what every Project Euler problem is about.'],
    ];
    const show = s => {
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      rowEls.forEach((tr, i) => {
        const visible = i <= Math.min(s, ROWS.length - 1);
        if (visible && !tr.dataset.timed) { timeRow(ROWS[i], tr); tr.dataset.timed = '1'; }
        tr.classList.toggle('on', visible);
      });
    };
    return stepped(ROWS.length, show);
  }

  // ======================================================== the Project Euler intro (data fills)

  function intro(slide) {
    const yearAgo = Math.max(...problems.map(p => p.n)) - 52;
    const older = problems.filter(p => p.solvers !== null && p.n <= yearAgo);
    const fewest = older.reduce((a, b) => (b.solvers < a.solvers ? b : a), older[0] || { solvers: 0, n: 0 });
    const first = problems.find(p => p.n === 1) || { solvers: 0 };
    fill(slide, 'total', fmt(problems.length));
    fill(slide, 'first-solvers', fmt(first.solvers || 0));
    fill(slide, 'fewest-solvers', fmt(fewest.solvers || 0));
    fill(slide, 'fewest-n', String(fewest.n));
    return stepped(0, () => {});
  }

  // ======================================================== the long pause: a calendar of solves

  function pause(slide) {
    const box = slide.querySelector('[data-role="visual"]');
    const months = new Map();
    for (const p of problems) {
      if (!p.solved || !p.date) continue;
      const key = p.date.getFullYear() * 12 + p.date.getMonth();
      months.set(key, (months.get(key) || 0) + 1);
    }
    const keys = [...months.keys()].sort((a, b) => a - b);
    let gap = { from: 0, to: 0, len: 0 };
    for (let i = 0; i + 1 < keys.length; i++) {
      const len = keys[i + 1] - keys[i] - 1;
      if (len > gap.len) gap = { from: keys[i] + 1, to: keys[i + 1] - 1, len };
    }
    const label = key => new Date(Math.floor(key / 12), key % 12, 1).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
    fill(slide, 'gap-from', label(gap.from));
    fill(slide, 'gap-to', label(gap.to + 1));
    fill(slide, 'gap-months', String(gap.len));

    const y0 = keys.length ? Math.floor(keys[0] / 12) : 2015, y1 = new Date().getFullYear();
    const CELL = 50, PITCH = 56, LEFT = 90, TOP = 40;
    const svg = el('svg', { viewBox: `0 0 ${LEFT + 12 * PITCH} ${TOP + (y1 - y0 + 1) * PITCH}`, role: 'img',
      'aria-label': 'Problems solved in each month since 2015' }, box);
    'JFMAMJJASOND'.split('').forEach((m, i) => {
      const t = el('text', { x: LEFT + i * PITCH + CELL / 2, y: TOP - 14, 'text-anchor': 'middle', class: 'chart-label' }, svg);
      t.textContent = m;
    });
    const peak = Math.max(1, ...months.values());
    for (let y = y0; y <= y1; y++) {
      const t = el('text', { x: LEFT - 16, y: TOP + (y - y0) * PITCH + CELL / 2 + 7, 'text-anchor': 'end', class: 'chart-label' }, svg);
      t.textContent = String(y);
      for (let m = 0; m < 12; m++) {
        const key = y * 12 + m, count = months.get(key) || 0;
        const cell = el('rect', { x: LEFT + m * PITCH, y: TOP + (y - y0) * PITCH, width: CELL, height: CELL, rx: 5,
          class: count ? 'pc-cell solved' : (key >= gap.from && key <= gap.to ? 'pc-cell gap' : 'pc-cell') }, svg);
        if (count) cell.style.opacity = String(0.35 + 0.65 * Math.sqrt(count / peak));
        const tip = el('title', {}, cell);
        tip.textContent = `${label(key)}: ${count} solved`;
      }
    }
    return stepped(0, () => {});
  }

  // ======================================================== what changed: the workshop in numbers

  function changed(slide) {
    const p = HISTORY.project || {};
    const ROWS = [
      [p.commands, 'shell commands, in a workshop that remembers where I left off'],
      [p.python, `solutions in Python, and ${fmt(p.c || 0)} of them also in C`],
      [p.notes, 'written explanations, one beside each solved problem'],
      [p.articles, `topic articles linking problems by technique (${fmt(p.articles_final || 0)} finished so far)`],
      [p.commits, 'commits, every change recorded'],
    ];
    const list = slide.querySelector('[data-role="list"]');
    for (const [n, text] of ROWS) {
      const row = h('div', 'wc-row', list);
      h('span', 'wc-n', row, Number.isInteger(n) ? fmt(n) : '–');
      h('span', 'wc-text', row, text);
    }
    return stepped(0, () => {});
  }

  // ======================================================== the vault

  const SAMPLE = `@runner.main
def solve(*args: str) -> str:
    n = runner.parse_int(args[0])
    if n == 1:
        return str(2)
    max_expected_value = int(n * math.log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + 2 * i * j] = 0
            except IndexError:
                break
    return str(2 * [i for i in numbers if i != 0][n - 2] + 1)`;

  /* Encrypt the sample for real (AES-GCM, a fresh random key) when WebCrypto is available. */
  async function cipherText(text) {
    const toB64 = bytes => btoa(String.fromCharCode(...bytes));
    try {
      const key = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, false, ['encrypt']);
      const iv = crypto.getRandomValues(new Uint8Array(12));
      const sealed = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(text)));
      return toB64(new Uint8Array([...iv, ...sealed]));
    } catch {
      return toB64(crypto.getRandomValues(new Uint8Array(Math.ceil(text.length * 0.8))));
    }
  }

  function vault(slide) {
    const code = slide.querySelector('[data-role="code"]');
    const label = slide.querySelector('[data-role="label"]');
    const stepEl = slide.querySelector('[data-role="step"]');
    const detailEl = slide.querySelector('[data-role="detail"]');
    const keys = slide.querySelector('[data-role="keys"]');
    const map = slide.querySelector('[data-role="map"]');
    const panes = [code.parentElement, keys, map];
    let token = 0, sealed = null;

    // the honour-code map: 1–100 open, the rest locked
    const COLS = 50, P = 13, C = 11;
    const svg = el('svg', { viewBox: `0 0 ${COLS * P} ${Math.ceil(problems.length / COLS) * P}`, role: 'img',
      'aria-label': 'Problems 1 to 100 open, the rest locked' }, map);
    problems.forEach((p, i) => el('rect', { x: (i % COLS) * P, y: Math.floor(i / COLS) * P, width: C, height: C, rx: 2,
      class: p.n <= 100 ? 'vm-open' : 'vm-locked' }, svg));

    async function scramble(my, animate) {
      sealed = sealed || await cipherText(SAMPLE);
      if (my !== token) return;
      const target = sealed.match(/.{1,48}/g).join('\n');
      if (!animate) { code.textContent = target; return; }
      const start = performance.now(), length = 1400;
      for (;;) {
        const t = Math.min(1, (performance.now() - start) / length);
        const cut = Math.floor(t * Math.max(SAMPLE.length, target.length));
        code.textContent = target.slice(0, cut) + SAMPLE.slice(cut);
        if (t >= 1) return;
        await frame();
        if (my !== token) return;
      }
    }

    const CAPTIONS = [
      ['On my machine, a solution reads like this.', 'This one is public: Problem 7, finding the 10,001st prime.'],
      ['In git, a private one looks like this.', 'Every solution past Problem 100 is encrypted before it leaves my machine. This is the same code, encrypted for real just now.'],
      ['Each person holds their own key.', 'One master key unlocks the solutions. Each collaborator gets their own sealed copy of it, opened only by their own key.'],
      ['The first 100 open, the rest locked.', 'Project Euler asks that answers past Problem 100 stay private. Here, the first 100 are open to read; everything after needs a key.'],
    ];
    const show = (s, animate) => {
      const my = ++token;
      [stepEl.textContent, detailEl.textContent] = CAPTIONS[s];
      panes.forEach((pane, i) => pane.classList.toggle('on', i === [0, 0, 1, 2][s]));
      label.textContent = s === 0 ? 'p0007_s0.py, as I edit it' : 'the same file, as git stores it';
      code.classList.toggle('sealed', s === 1);
      if (s === 0) code.textContent = SAMPLE;
      if (s === 1) scramble(my, animate);
    };
    return stepped(3, show, () => { token++; });
  }

  // ======================================================== working with AI (static)

  function ai() { return stepped(0, () => {}); }

  // ======================================================== live demo: pick a problem

  function demo(slide) {
    const numEl = slide.querySelector('[data-role="number"]');
    const titleEl = slide.querySelector('[data-role="title"]');
    const metaEl = slide.querySelector('[data-role="meta"]');
    const byNumber = new Map(problems.map(p => [p.n, p]));
    let token = 0;
    const describe = n => {
      const p = byNumber.get(n);
      titleEl.textContent = p ? p.title : '';
      const mine = p && p.solved && p.date
        ? `, including me on ${p.date.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}` : '';
      metaEl.textContent = p && p.solvers !== null ? `Solved by ${fmt(p.solvers)} people${mine}.` : '';
    };
    async function draw(my, animate) {
      const pick = 1 + Math.floor(Math.random() * 100);
      titleEl.textContent = ''; metaEl.textContent = '';
      if (animate) {
        for (let i = 0; i < 18; i++) {
          numEl.textContent = String(1 + Math.floor(Math.random() * 100));
          await sleep(40 + i * 9);
          if (my !== token) return;
        }
      }
      numEl.textContent = String(pick);
      describe(pick);
    }
    const show = (s, animate) => {
      const my = ++token;
      slide.classList.toggle('drawn', s === 1);
      if (s === 0) { numEl.textContent = '?'; titleEl.textContent = ''; metaEl.textContent = ''; }
      else draw(my, animate);
    };
    return stepped(1, show, () => { token++; });
  }

  window.DECK_PARTS = Object.assign(window.DECK_PARTS || {}, { opener, intro, pause, changed, vault, ai, demo });
})();
