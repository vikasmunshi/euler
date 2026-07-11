/* Shell chrome behaviour (site-design §1/§6) — same-origin, CSP-clean, no deps.
   Loaded without defer from <head> so a stored data-theme applies before first
   paint; everything else is wired on DOMContentLoaded / delegated clicks. */
(function () {
  'use strict';
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem('theme'); } catch (e) { /* private mode */ }
  if (stored === 'light' || stored === 'dark') { root.dataset.theme = stored; }

  // MathJax v3 config — this file loads before the deferred /vendor/mathjax
  // bundle, so the loader reads it on init. Statements and notes carry TeX as
  // $…$ / $$…$$ text (convention_documentation.md); \$ escapes a literal dollar.
  // MathJax's defaults already skip pre/code/textarea, so source views and the
  // editors are never typeset.
  window.MathJax = {
    tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']], processEscapes: true },
    // matchFontHeight measures the surrounding font's x-height and inflates the
    // math (~20% over system-ui), and the measurement varies with load timing —
    // the "large math until a refresh" symptom. Off = deterministic: math
    // renders at exactly the surrounding font size, every client, every load.
    chtml: { scale: 1, matchFontHeight: false }
  };

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

  // htmx swaps replace pane content after MathJax's initial pass — re-typeset
  // the left pane (its math state first cleared so removed nodes are forgotten).
  document.addEventListener('htmx:afterSwap', function () {
    if (window.MathJax && MathJax.typesetPromise) {
      if (MathJax.typesetClear) { MathJax.typesetClear(); }
      MathJax.typesetPromise([document.getElementById('content')]);
    }
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
    // data-popup links (footer documents, account, change password) open in a
    // small popup window, leaving the shell — and the terminal — untouched.
    var popup = ev.target.closest('a[data-popup]');
    if (popup) {
      ev.preventDefault();
      window.open(popup.href, 'euler-doc', 'popup=yes,width=760,height=840');
    }
  });

  // A deliberate exit (logout) should not trip the terminal's beforeunload
  // guard: tell the /terminal iframe to disarm before the shell navigates
  // (the guard itself arrives with the Phase 6 terminal; the contract is here).
  document.addEventListener('submit', function (ev) {
    if (!ev.target.matches('form[action="/auth/logout"]')) { return; }
    var terminal = document.getElementById('terminal');
    if (terminal && terminal.contentWindow) {
      terminal.contentWindow.postMessage({ euler: 'disarm' }, window.location.origin);
    }
  });
})();
