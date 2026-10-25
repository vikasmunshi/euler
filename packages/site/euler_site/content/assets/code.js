// The code viewer (/code/, web-server-guide § The code viewer): the page's one script.
//
// Loaded in <head>, not deferred, so the theme is set before the first paint: the stored
// choice, else the system's. The rest waits for the DOM — the tree filter, and on a
// phone the Files drawer. Everything else on the page (file links, #L<n> line links, the
// highlighted line) is plain HTML and CSS and works without it.
(function () {
  'use strict';

  var root = document.documentElement;
  root.classList.add('js');

  // ── theme ────────────────────────────────────────────────────────────────────────
  // The key is the main site's (site.js), so one choice holds on both. localStorage may
  // be absent or throw (a private window, blocked site data): then the toggle still
  // works, it just is not remembered.
  var KEY = 'euler-theme';
  function stored() { try { return window.localStorage.getItem(KEY); } catch (e) { return null; } }
  function store(value) { try { window.localStorage.setItem(KEY, value); } catch (e) { /* not kept */ } }
  var dark = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  function apply(theme) { root.setAttribute('data-theme', theme); }
  apply(stored() || (dark && dark.matches ? 'dark' : 'light'));
  if (dark && dark.addEventListener) {
    dark.addEventListener('change', function (e) { if (!stored()) { apply(e.matches ? 'dark' : 'light'); } });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.querySelector('.theme-toggle');
    function label() {
      var isDark = root.getAttribute('data-theme') === 'dark';
      toggle.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    }
    label();
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      apply(next);
      store(next);
      label();
    });

    var body = document.body;
    var files = document.getElementById('files');
    var tree = files.querySelector('.tree');
    var filter = document.getElementById('filter');
    var count = files.querySelector('.filter-count');
    var opener = document.querySelector('.files-toggle');
    var current = tree.querySelector('a[aria-current]');

    // The open file, centred in the tree's own scroll box (never the page's).
    function reveal() {
      if (!current) { return; }
      var box = files.getBoundingClientRect();
      files.scrollTop += current.getBoundingClientRect().top - box.top - files.clientHeight / 2;
    }
    reveal();

    // ── the drawer (phone width only: CSS decides whether it is one) ────────────────
    function setOpen(open) {
      body.classList.toggle('files-open', open);
      opener.setAttribute('aria-expanded', String(open));
      if (open) { reveal(); filter.focus(); } else { opener.focus(); }
    }
    opener.addEventListener('click', function () { setOpen(true); });
    files.querySelector('.files-close').addEventListener('click', function () { setOpen(false); });
    document.querySelector('.scrim').addEventListener('click', function () { setOpen(false); });
    files.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && body.classList.contains('files-open')) { setOpen(false); }
    });

    // ── the filter ───────────────────────────────────────────────────────────────────
    // A query matches a file's name or its summary; one with a `/` in it matches the
    // whole path. Matching files show with their folders opened; everything else hides.
    // Cleared, the tree goes back to how it was.
    var links = Array.prototype.slice.call(tree.querySelectorAll('a[data-path]'));
    var folders = Array.prototype.slice.call(tree.querySelectorAll('details'));
    var wasOpen = folders.map(function (d) { return d.open; });
    var rows = Array.prototype.slice.call(tree.querySelectorAll('li'));

    function name(a) { var path = a.getAttribute('data-path'); return path.slice(path.lastIndexOf('/') + 1); }
    function mark(a, q) {
      var text = name(a);
      var at = q && q.indexOf('/') < 0 ? text.toLowerCase().indexOf(q) : -1;
      a.textContent = '';
      if (at < 0) { a.textContent = text; return; }
      // One span for the whole name: the row is a flex box, and loose pieces would each
      // be an item of their own, spaced apart by its gap.
      var label = document.createElement('span');
      var hit = document.createElement('mark');
      hit.textContent = text.slice(at, at + q.length);
      label.append(text.slice(0, at), hit, text.slice(at + q.length));
      a.append(label);
    }

    function run() {
      var q = filter.value.trim().toLowerCase();
      if (!q) {
        rows.forEach(function (li) { li.hidden = false; });
        folders.forEach(function (d, i) { d.open = wasOpen[i]; });
        links.forEach(function (a) { mark(a, ''); });
        count.hidden = true;
        return;
      }
      rows.forEach(function (li) { li.hidden = true; });
      var matches = 0;
      links.forEach(function (a) {
        var hay = q.indexOf('/') >= 0 ? a.getAttribute('data-path') : name(a) + '\n' + (a.title || '');
        var hit = hay.toLowerCase().indexOf(q) >= 0;
        mark(a, hit ? q : '');
        if (!hit) { return; }
        matches += 1;
        for (var el = a.parentElement; el && el !== tree; el = el.parentElement) {
          if (el.tagName === 'LI') { el.hidden = false; }
          if (el.tagName === 'DETAILS') { el.open = true; }
        }
      });
      count.textContent = matches === 0 ? 'No files match' : matches + (matches === 1 ? ' file matches' : ' files match');
      count.hidden = false;
    }
    filter.addEventListener('input', run);
    // Enter opens the first match, so a name typed in full is one keystroke from its file.
    filter.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' || !filter.value.trim()) { return; }
      var first = links.filter(function (a) { return !a.closest('li[hidden]'); })[0];
      if (first) { e.preventDefault(); window.location.href = first.href; }
    });
  });
})();
