/* The developer section's one stepped slide: command blocks and the canonical form the real
   lexer (solver/shell/lexer.py) turns them into, captured verbatim from `lex()`.
   Registers itself on window.DECK_PARTS (data-viz="lang"). */
(() => {
  'use strict';

  const EXAMPLES = [
    ['eval 42 && benchmark 42',
      'None:\n{\n    True: _ = eval 42;\n    {rcode} == 0: _ = benchmark 42;\n}',
      '&& becomes a guard: the second command runs only if the first exited 0.'],
    ['git-sync || git-status',
      'None:\n{\n    True: _ = git-sync;\n    {rcode} != 0: _ = git-status;\n}',
      '|| is the same guard, inverted.'],
    ['x = {next} + 1',
      'None:\n{\n    True: x = {next} + 1;\n}',
      'Assignments and bare expressions are statements too: a falsy expression exits 1, so it can gate a chain.'],
    ['loop {solved}: eval {loop.number} && benchmark {loop.number}',
      '{solved}:\n{\n    True: _ = eval {loop.number};\n    {rcode} == 0: _ = benchmark {loop.number};\n}',
      'A loop is part of the language: the header names the list, {loop} is the current element.'],
  ];

  function controller(slide) {
    const input = slide.querySelector('[data-role="input"]');
    const canonical = slide.querySelector('[data-role="canonical"]');
    const note = slide.querySelector('[data-role="note"]');
    const last = EXAMPLES.length - 1;
    let step = 0;
    const show = s => {
      step = s;
      [input.textContent, canonical.textContent, note.textContent] = EXAMPLES[s];
    };
    return {
      enter(direction) { show(direction < 0 ? last : 0); },
      leave() {},
      next() { if (step >= last) return false; show(step + 1); return true; },
      prev() { if (step <= 0) return false; show(step - 1); return true; },
      replay() { show(step); },
      jump(s) { show(Math.max(0, Math.min(last, s))); },
    };
  }

  window.DECK_PARTS = window.DECK_PARTS || {};
  window.DECK_PARTS.lang = controller;
})();
