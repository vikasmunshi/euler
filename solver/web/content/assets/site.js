/* Theme toggle (site-design §2): dark is the default; an explicit choice is
   stamped as data-theme on <html> and persisted. Loaded without defer from
   <head> so a stored choice applies before first paint (no flash); the button
   itself is wired on DOMContentLoaded. Same-origin, CSP-clean. */
(function () {
  'use strict';
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem('theme'); } catch (e) { /* private mode */ }
  if (stored === 'light' || stored === 'dark') { root.dataset.theme = stored; }

  document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('theme-toggle');
    if (!button) { return; }
    button.addEventListener('click', function () {
      var current = root.dataset.theme ||
        (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
      var next = current === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
    });
  });
})();
