/* Shell chrome behaviour (web-server-guide § The site) — same-origin, CSP-clean, no deps.
   Loaded from <head> without defer so the MathJax config below is in place before
   the deferred typesetter reads it; everything else is wired on DOMContentLoaded
   or delegated clicks.

   Loaded by both tiers: the signed-out pages render the same shell, where the
   hooks below simply find nothing to bind (no editors, no terminal, no vault). */
(function () {
  'use strict';

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

  // Every off-site link opens in a new tab: following one in-place would tear
  // down the shell — and with it the terminal in the right pane, which is the
  // one thing the design promises never to lose. Applied document-wide (not per
  // link), so it holds for markup we do not author: the cached projecteuler.net
  // statements, generated notes, and the markdown docs alike.
  function externalize(root) {
    (root || document).querySelectorAll('a[href]:not([target])').forEach(function (a) {
      var url;
      try { url = new URL(a.getAttribute('href'), window.location.href); } catch (e) { return; }
      if (url.protocol !== 'http:' && url.protocol !== 'https:') { return; }  // mailto:, #frag
      if (url.host === window.location.host) { return; }
      a.target = '_blank';
      a.rel = (a.rel ? a.rel + ' ' : '') + 'noopener noreferrer';
    });
  }
  document.addEventListener('DOMContentLoaded', function () { externalize(document); });

  // htmx swaps replace pane content after MathJax's initial pass — re-typeset
  // the left pane (its math state first cleared so removed nodes are forgotten).
  document.addEventListener('htmx:afterSwap', function () {
    if (window.MathJax && MathJax.typesetPromise) {
      if (MathJax.typesetClear) { MathJax.typesetClear(); }
      MathJax.typesetPromise([document.getElementById('content')]);
    }
    enhanceEditors();
    externalize(document);
  });

  // ── the pane's back arrow (web-server-guide § The site) ─────────────────────────────────
  // The address bar's back button navigates the *document*, which tears down the
  // right pane's terminal — the session the shell promises never to lose. So the
  // header carries a back of its own over the pages #content has shown: a swap,
  // not a navigation, so the terminal never notices.
  //
  // The stack is the pane's, not the browser's. htmx pushes a URL for every pane
  // navigation (hx-push-url), and that push is the signal a new page landed. The
  // arrow's own swap pushes its URL directly (below) rather than through htmx, so
  // it never lands here — going back pops, it does not stack.
  var paneStack = [];

  function panePath() { return window.location.pathname + window.location.search; }

  //: The page behind the current one — or, on the first page of a visit, itself.
  function backTarget() {
    return paneStack.length > 1 ? paneStack[paneStack.length - 2] : (paneStack[0] || '/');
  }

  function refreshBack() {
    var back = document.getElementById('nav-back');
    if (!back) { return; }                              // the terminal frame has no header
    var target = backTarget();
    back.setAttribute('href', target);                  // a real href: no-JS, middle-click
    back.classList.toggle('is-first', paneStack.length < 2);
    back.title = paneStack.length > 1 ? 'back to ' + target : 'back';
  }

  function paneBack() {
    var target = backTarget();
    if (paneStack.length > 1) { paneStack.pop(); }      // leave the page we are on
    // htmx binds hx-get at process time, so the arrow cannot carry a target that
    // changes on every navigation — it asks htmx for the swap directly instead, and
    // pushes the URL itself (htmx.ajax does not, and the address bar must keep up).
    window.htmx.ajax('GET', target, { target: '#content', swap: 'innerHTML' })
      .then(function () {
        window.history.pushState({}, '', target);
        refreshBack();
      });
  }

  document.addEventListener('htmx:pushedIntoHistory', function (ev) {
    var path = (ev.detail && ev.detail.path) || panePath();
    if (paneStack[paneStack.length - 1] !== path) { paneStack.push(path); }
    refreshBack();
  });

  // A browser back/forward still works (htmx restores the pane) — but its history
  // is not ours, so re-seed rather than let the two drift apart.
  window.addEventListener('popstate', function () {
    paneStack = [panePath()];
    refreshBack();
  });

  document.addEventListener('DOMContentLoaded', function () {
    paneStack = [panePath()];                           // a fresh document: nothing behind us
    refreshBack();
  });

  // Lazy-load the CodeMirror editor only when an edit page appears in the pane —
  // its vendored graph (~630 KB) never loads on other pages. The module is cached
  // after first import; each visit just (re)mounts on the fresh textarea.
  var cm = null;
  function enhanceEditors() {
    var pane = document.getElementById('content') || document;
    if (!pane.querySelector('textarea.editor-buffer[data-cm]')) { return; }
    if (cm) { cm.mount(pane); return; }
    import('/assets/editor.js').then(function (m) { cm = m; m.mount(pane); })
      .catch(function () { /* no-JS/blocked: the plain textarea still works */ });
  }
  document.addEventListener('DOMContentLoaded', enhanceEditors);

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
    // The header's back arrow: a swap, never a document navigation (its href is
    // the no-JS fallback, and what a middle-click opens in a new tab).
    if (ev.target.closest('#nav-back') && window.htmx && !ev.metaKey && !ev.ctrlKey) {
      ev.preventDefault();
      paneBack();
    }
  });

  // A deliberate exit (logout) should not trip the terminal's beforeunload
  // guard: tell the /terminal iframe to disarm before the shell navigates.
  // Also forget the vault password key — the session it unlocked is ending.
  document.addEventListener('submit', function (ev) {
    if (!ev.target.matches('form[action="/auth/logout"]')) { return; }
    if (window.Vault) { window.Vault.clear(); }
    var terminal = document.getElementById('terminal');
    if (terminal && terminal.contentWindow) {
      terminal.contentWindow.postMessage({ euler: 'disarm' }, window.location.origin);
    }
  });

  // ── the user menu's terminal control ───────────────────────────────────────
  // One item, not two: it names the act it offers ("Disconnect terminal") and the
  // dot beside it carries the state. Connecting and disconnecting are always the
  // USER'S acts — the terminal never reconnects on its own — so this posts the act
  // into the /terminal iframe and waits to be told what happened, rather than
  // assuming it worked. The iframe reports its state back (terminal.js), which is
  // what `termState` below listens for; until it does, the item keeps its label.
  var termConnected = true;

  function paintTerminalToggle() {
    var button = document.getElementById('term-toggle');
    var dot = document.getElementById('term-dot');
    if (!button || !dot) { return; }             // no terminal in this shell (signed out)
    // childNodes[0] is the label text node — the dot is an element after it, and
    // textContent would take the dot with it.
    button.childNodes[0].nodeValue = (termConnected ? 'Disconnect terminal' : 'Connect terminal') + ' ';
    dot.className = 'dot ' + (termConnected ? 'on' : 'off');
  }

  document.addEventListener('click', function (ev) {
    var button = ev.target.closest && ev.target.closest('#term-toggle');
    if (!button) { return; }
    var terminal = document.getElementById('terminal');
    if (terminal && terminal.contentWindow) {
      terminal.contentWindow.postMessage(
        { euler: termConnected ? 'disconnect' : 'connect' }, window.location.origin);
    }
    var menu = button.closest('details');
    if (menu) { menu.open = false; }
  });

  // The iframe's own report of where it stands: the toggle follows the terminal,
  // never the other way round. A session that drops on its own (the shell exits,
  // the socket dies) lands here too, so the menu never claims a live terminal
  // that is not there.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== window.location.origin || !ev.data || ev.data.euler !== 'term-state') { return; }
    termConnected = !!ev.data.connected;
    paintTerminalToggle();
  });

  // ── the vault: auto-unlock + account-panel recovery ────────────────
  // Sign-in stashed PK (vault.js); unlock the per-user service's session with it
  // once per page load. Fire-and-forget: 'stale'/'error' just leave the vault
  // locked, and the account panel shows the recovery form below.
  document.addEventListener('DOMContentLoaded', function () {
    if (window.Vault) { window.Vault.unlock(); }
  });

  // The recovery form (#vault-recover, in the /account/vault fragment): the user
  // types a password; its PK is derived with the VAULT's own salt + iterations
  // (/vault/status). If that password is simply the current one (the instance
  // restarted since sign-in) the unlock succeeds directly; if it is the OLD
  // password after a change made elsewhere, re-wrap VK across to the current
  // sign-in's PK when we hold one. Delegated: the fragment is htmx-swapped.
  document.addEventListener('submit', function (ev) {
    var form = ev.target.closest && ev.target.closest('#vault-recover');
    if (!form || !window.Vault) { return; }
    ev.preventDefault();
    var errorBox = form.querySelector('#vault-recover-error');
    var fail = function (message) { errorBox.textContent = message; errorBox.hidden = false; };
    var password = form.querySelector('#vault-recover-password').value;
    (async function () {
      try {
        var status = await fetch('/vault/status', { credentials: 'same-origin' });
        if (!status.ok) { return fail('vault status unavailable'); }
        var info = await status.json();
        if (!info.vault) { return fail('no vault to unlock'); }
        var pk = await Vault.derivePk(password, info.salt, info.iterations);
        var creds = Vault.stored();
        var resp;
        if (creds && creds.pk !== pk) {
          // an old password: carry the vault forward to the current sign-in's PK
          resp = await Vault.postJson('/vault/rewrap',
            { old_pk: pk, new_pk: creds.pk, new_salt: creds.salt });
        } else {
          resp = await Vault.postJson('/vault/unlock', { pk: pk, salt: info.salt });
        }
        if (resp.status === 409) { return fail('that password does not unlock this vault'); }
        if (!resp.ok) { return fail('unlock failed — try again'); }
        if (window.htmx) {
          window.htmx.ajax('GET', '/account/vault', { target: '#vault-panel' });
        }
      } catch (err) {
        fail('unlock failed: ' + (err && err.message ? err.message : 'unexpected error'));
      }
    })();
  });

  // ── the terminal drives the left pane ──────────────────────────────────────
  // `show` / `edit` in a web shell emit an OSC 5379 sequence on the PTY; the
  // terminal document turns it into {euler: 'navigate', path} and posts it here
  // (it never touches this DOM itself). We swap the pane exactly as a link would
  // — same htmx target, same pushed URL — so the back arrow's stack stays honest
  // and the terminal, which is not part of #content, is untouched.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== window.location.origin || !ev.data || ev.data.euler !== 'navigate') { return; }
    var path = String(ev.data.path || '');
    if (path.charAt(0) !== '/' || path.charAt(1) === '/') { return; }   // same-origin paths only
    if (!window.htmx) { window.location.assign(path); return; }         // no-JS-htmx fallback
    window.htmx.ajax('GET', path, { target: '#content', swap: 'innerHTML' })
      .then(function () {
        window.history.pushState({}, '', path);
        if (paneStack[paneStack.length - 1] !== path) { paneStack.push(path); }
        refreshBack();
      });
  });
})();
