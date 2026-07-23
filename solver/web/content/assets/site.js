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
    // A swapped-in pane may carry terminal controls of its own (the start page's
    // Terminal card): they arrive with the server's static markup and know nothing
    // of the live socket, so paint them from the state we hold.
    paintTerminalControls();
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
    var refresh = document.getElementById('nav-refresh');
    if (refresh) { refresh.setAttribute('href', panePath()); }   // no-JS / middle-click fallback
  }

  // Refresh the content pane in place: re-fetch the current URL into #content. The terminal is a
  // separate pane (#ws), so it is untouched — this is the pane's own reload, not the document's.
  // No history push and no stack change: it re-renders the same page, it does not navigate.
  function paneRefresh() {
    window.htmx.ajax('GET', panePath(), { target: '#content', swap: 'innerHTML' });
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
    // The header's refresh: a pane swap, never a document reload (which would drop the terminal).
    if (ev.target.closest('#nav-refresh') && window.htmx && !ev.metaKey && !ev.ctrlKey) {
      ev.preventDefault();
      paneRefresh();
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

  // ── the terminal controls ──────────────────────────────────────────────────
  // Any number of controls, one state. A control is [data-term-toggle]: it names
  // the act it offers on its [data-term-label] and carries the state on its
  // [data-term-dot]. Two exist today — the user menu's item (always there, in the
  // header) and the start page's Terminal card (in the swappable pane) — and both
  // are painted from the one `termConnected` below, so they can never disagree.
  //
  // Connecting and disconnecting are always the USER'S acts (the terminal never
  // reconnects on its own), so a click posts the act into the /terminal iframe and
  // waits to be TOLD what happened rather than assuming it worked.
  //
  // The state starts false and is painted immediately: the shell may not have a
  // terminal at all (signed out), the socket may fail to open, and a control that
  // claims a live session before the iframe has reported one is a lie we would
  // have no way to correct. The first report (the page-load connect) flips it.
  var termConnected = false;

  function paintTerminalControls() {
    document.querySelectorAll('[data-term-label]').forEach(function (label) {
      label.textContent = termConnected ? 'Disconnect' : 'Connect';
    });
    document.querySelectorAll('[data-term-dot]').forEach(function (dot) {
      dot.className = 'dot ' + (termConnected ? 'on' : 'off');
    });
    // The git menu's verbs type into the shell, so they need one to be there. This
    // is the same single state, not a second reading of the socket: the panel joins
    // the set above rather than tracking the terminal on its own. The chip's branch
    // state is untouched — that is read server-side and owes the socket nothing.
    document.querySelectorAll('.git-menu').forEach(function (menu) {
      menu.classList.toggle('git-offline', !termConnected);
    });
  }
  document.addEventListener('DOMContentLoaded', paintTerminalControls);

  //: Post an act into the terminal iframe. Unframed (or signed out) there is none.
  function postToTerminal(message) {
    var terminal = document.getElementById('terminal');
    if (terminal && terminal.contentWindow) {
      terminal.contentWindow.postMessage(message, window.location.origin);
    }
  }

  document.addEventListener('click', function (ev) {
    var button = ev.target.closest && ev.target.closest('[data-term-toggle]');
    if (!button) { return; }
    postToTerminal({ euler: termConnected ? 'disconnect' : 'connect' });
    var menu = button.closest('details');
    if (menu) { menu.open = false; }
  });

  // The account page's tool rows: a click types the command that fixes the row into
  // the shell (`git-identity`, `! claude /login`). The web shell is the front door
  // for these — the logins are interactive and belong in a terminal, not in a form
  // that would have to handle a credential — so the button carries the user there
  // rather than pretending to do it for them.
  document.addEventListener('click', function (ev) {
    var button = ev.target.closest && ev.target.closest('[data-term-cmd]');
    if (!button) { return; }
    // A disconnected terminal drops the frame (terminal.js's send()), so the git
    // menu paints itself offline and says so rather than letting a click do nothing
    // silently. Honour that here: the panel's own note is the answer, not a command
    // shouted into a closed socket.
    if (button.closest('.git-offline')) { return; }
    postToTerminal({ euler: 'run', command: button.getAttribute('data-term-cmd') });
    // The verb's answer belongs in the terminal, so close the menu that is now
    // covering it. The chip itself refreshes when the shell says so (§ git-changed).
    var menu = button.closest('details');
    if (menu) { menu.open = false; }
  });

  // The iframe's own report of where it stands: the controls follow the terminal,
  // never the other way round. A session that drops on its own (the shell exits,
  // the socket dies) lands here too, so nothing claims a live terminal that is not
  // there.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== window.location.origin || !ev.data || ev.data.euler !== 'term-state') { return; }
    termConnected = !!ev.data.connected;
    paintTerminalControls();
  });

  // ── the git chip's refresh (OSC 5379 `git`) ────────────────────────────────
  // The header reads its git state once per navigation and never polls — but the
  // git commands run in the TERMINAL, and that is not a navigation. So the shell
  // says when it moved (solver/core/osc.py → terminal.js → here) and the chip
  // re-reads itself: one `git status`, at the one moment the state changed.
  //
  // The event is dispatched on <body> because the chip listens for it `from:body`
  // and swaps ITSELF (hx-swap="outerHTML") — a fresh #git replaces the stale one
  // without touching the pane or the terminal. Firing an event rather than calling
  // htmx.ajax keeps the fetch declarative, in the markup, next to the element it
  // replaces.
  //
  // It fires for a hand-typed `git-sync` exactly as for the menu's item: the menu
  // types the same command, so there is one path here, not two.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== window.location.origin || !ev.data || ev.data.euler !== 'git-changed') { return; }
    document.body.dispatchEvent(new CustomEvent('euler:git-changed'));
  });

  // ── the account panel's refresh (OSC 5379 `account`) ───────────────────────
  // A command that changes what /account shows about you — `user` (a new identity),
  // `git-identity` (a GitHub sign-in) — runs in the terminal, not via a navigation,
  // so it nudges the page the same way a git command does. The listener that acts on
  // it (`euler:account-changed from:body`) lives INSIDE the account fragment, on
  // #vault-panel — so this reaches nothing, and costs nothing, unless /account is the
  // visible pane. (git-sync / git-filter change decrypt access too, but they already
  // fire git-changed, which #vault-panel also listens for — so no command emits both.)
  window.addEventListener('message', function (ev) {
    if (ev.origin !== window.location.origin || !ev.data || ev.data.euler !== 'account-changed') { return; }
    document.body.dispatchEvent(new CustomEvent('euler:account-changed'));
  });

  // ── copy buttons ───────────────────────────────────────────────────────────
  // [data-copy] holds the text (the public key today). The label's flip to
  // "Copied" is the only feedback that the clipboard actually took it.
  document.addEventListener('click', function (ev) {
    var button = ev.target.closest && ev.target.closest('[data-copy]');
    if (!button || !navigator.clipboard) { return; }
    navigator.clipboard.writeText(button.getAttribute('data-copy')).then(function () {
      var was = button.textContent;
      button.textContent = 'Copied';
      setTimeout(function () { button.textContent = was; }, 1200);
    }, function () { button.textContent = 'Copy failed'; });
  });

  // ── the vault: auto-unlock + account-panel recovery ────────────────
  // Sign-in stashed PK (vault.js); unlock the per-user service's session with it
  // once per page load. Fire-and-forget: 'stale'/'error' just leave the vault
  // locked, and the account panel shows the recovery form below.
  document.addEventListener('DOMContentLoaded', function () {
    if (!window.Vault) { return; }
    window.Vault.unlock().then(function (result) {
      // The chip renders server-side on this load, BEFORE this unlock runs — so its
      // worktree scan (git status over solutions/private, which needs the master key)
      // may have failed against a still-locked vault. A successful unlock means that
      // scan can now succeed: nudge the chip to re-read, over the same git-changed
      // path the shell's git commands use. Only on a real unlock, so a page whose
      // vault was already open pays nothing.
      if (result === 'unlocked') {
        document.body.dispatchEvent(new CustomEvent('euler:git-changed'));
      }
    });
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
