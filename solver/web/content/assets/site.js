/* Shell chrome behaviour (site-design §1/§6) — same-origin, CSP-clean, no deps.
   Loaded without defer from <head> so a stored data-theme applies before first
   paint; everything else is wired on DOMContentLoaded / delegated clicks. */
(function () {
  'use strict';
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem('theme'); } catch (e) { /* private mode */ }
  if (stored === 'light' || stored === 'dark') { root.dataset.theme = stored; }

  function currentTheme() {
    return root.dataset.theme ||
      (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  }

  document.addEventListener('DOMContentLoaded', function () {
    // The header slider: checked = dark (the primary design), remembered per user.
    var toggle = document.getElementById('theme-toggle');
    if (!toggle) { return; }
    toggle.checked = currentTheme() === 'dark';
    toggle.addEventListener('change', function () {
      var next = toggle.checked ? 'dark' : 'light';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
    });
  });

  document.addEventListener('click', function (ev) {
    // Native <details> dropdowns (Actions, user menu): close on selection or
    // on any click outside the open menu.
    document.querySelectorAll('details.menu[open]').forEach(function (menu) {
      if (!menu.contains(ev.target) || ev.target.closest('a, button')) {
        menu.removeAttribute('open');
      }
    });
    // The Actions menu's Save submits the pane's editor form.
    if (ev.target.closest('[data-action="submit-editor"]')) {
      var form = document.querySelector('#content form.editor-form');
      if (form) { form.requestSubmit(); }
    }
  });
})();
