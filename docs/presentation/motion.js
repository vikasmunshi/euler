/* Whether the deck animates: the one place that decides, read by every other script.
   The deck honours a system that asks for reduced motion. A presenter on a machine set that way
   can override it for this deck alone, with the Motion button or the M key: the choice stays in
   this browser, and the stylesheet's reduced-motion rules stand aside for .motion-on. */
(() => {
  'use strict';

  const KEY = 'euler-deck-motion';
  const system = window.matchMedia('(prefers-reduced-motion: reduce)');
  // storage can throw (blocked site data); the deck then simply forgets the choice on reload
  const stored = () => { try { return localStorage.getItem(KEY) === 'on'; } catch { return false; } };
  const store = on => {
    try {
      if (on) localStorage.setItem(KEY, 'on'); else localStorage.removeItem(KEY);
    } catch { /* see above */ }
  };
  let forced = stored();
  const mark = () => document.documentElement.classList.toggle('motion-on', forced);
  mark();

  window.DECK_MOTION = {
    /* The system asks for less motion, so there is something to override. */
    get asked() { return system.matches; },
    get forced() { return forced; },
    get reduced() { return system.matches && !forced; },
    toggle() {
      forced = !forced;
      store(forced);
      mark();
    },
  };
})();
