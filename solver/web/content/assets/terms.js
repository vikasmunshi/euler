/* Terms stage: the accept checkbox unlocks only once the terms box has been
 * scrolled to the end (or immediately when the text fits without scrolling). */
'use strict';

(() => {
  const box = document.getElementById('terms-box');
  const accept = document.getElementById('accept-box');
  const hint = document.getElementById('terms-hint');
  if (!box || !accept) return;

  function unlock() {
    accept.disabled = false;
    if (hint) hint.hidden = true;
    box.removeEventListener('scroll', onScroll);
  }

  function atEnd() {
    return box.scrollTop + box.clientHeight >= box.scrollHeight - 4;
  }

  function onScroll() {
    if (atEnd()) unlock();
  }

  if (atEnd()) unlock();               // fits without scrolling
  else box.addEventListener('scroll', onScroll, { passive: true });
})();
