/* The right pane's terminal (web-server-guide § The site).

   Its own document, framed by the app shell at #ws, so htmx swaps, content-page
   JS, and history restores structurally cannot touch the session. It talks only
   to /ws — xterm.js in, raw PTY bytes out — and to its parent, by postMessage:

   - down (parent → here): {euler: 'disarm'} before a deliberate exit (logout),
     so the beforeunload guard does not fire on a navigation the user chose;
     {euler: 'connect'|'disconnect'} from the user menu's terminal item;
   - up (here → parent): {euler: 'navigate', path} when the shell's `show`/`edit`
     emits its OSC 5379 sequence — the shell drives the left pane, and only ever
     through the parent (this document never touches the parent's DOM);
     {euler: 'term-state', connected} whenever the socket opens or closes, so the
     user menu's item can name the act it offers.

   Wire protocol (solver/web/ws/app.py): binary frames are raw PTY bytes both
   ways; a text frame {"resize": [cols, rows]} carries the geometry. */
(function () {
  'use strict';

  var host = document.getElementById('term');
  if (!host || typeof window.Terminal !== 'function') { return; }

  // ── theme ────────────────────────────────────────────────────────────────
  // Literal hex, not the site's CSS tokens: what renders here is the *shell's own*
  // output, and the shell paints with absolute xterm-256 indices chosen for a dark
  // terminal (near-whites like 254/247 for body text, 238 for rules). Its darkness
  // is the shell's constraint, not the site's choice — the site being dark-only
  // means the two agree today, but this must not start following a palette the
  // shell's ANSI indices know nothing about. The values are the dark tokens.
  var term = new window.Terminal({
    cursorBlink: true,
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
    fontSize: 13,
    // A small lineHeight bump gives the underscore descender room (else a typed
    // '_' is clipped to the cell's bottom pixel row and renders blank).
    lineHeight: 1.15,
    scrollback: 5000,
    theme: {
      background: '#171a21',            // --surface (dark)
      foreground: '#e5e7eb',            // --text (dark)
      cursor: '#f97316',                // --accent
      cursorAccent: '#171a21',
      selectionBackground: 'rgba(249,115,22,0.35)'
    }
  });
  var fit = new window.FitAddon.FitAddon();
  term.loadAddon(fit);
  term.open(host);
  fit.fit();

  // ── the socket ───────────────────────────────────────────────────────────
  // Connect and disconnect are the USER'S acts (the ☰ user menu; the first
  // connect rides the page load). There is deliberately no automatic reconnect:
  // a dropped transport stays dropped, visibly, until the user asks — the
  // server-side shell survives a disconnect and replays on the next attach.
  var socket = null;
  var closedByUs = false;

  //: Tell the shell where we stand. The user menu's terminal item follows this and
  //: never the other way round: a session that drops on its own (the shell exits,
  //: the transport dies) must not leave the menu offering to disconnect something
  //: that is already gone. Unframed (a direct visit to /terminal) there is no one
  //: to tell.
  function report(connected) {
    if (window.parent !== window) {
      window.parent.postMessage({ euler: 'term-state', connected: connected }, location.origin);
    }
  }
  //: False while the server's replay is still being parsed: the scrollback is
  //: drawn, but the commands in it already ran, so their control sequences must
  //: not fire again (§ the OSC handler below).
  var live = false;

  function connect() {
    if (socket) { return; }             // already connected / connecting
    closedByUs = false;
    var url = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';
    socket = new WebSocket(url);
    socket.binaryType = 'arraybuffer';

    socket.onopen = function () {
      live = false;                     // a fresh attach replays before it streams
      arm();
      report(true);
      sendSize();                       // the server's PTY starts at 80x24
    };
    // Output is raw PTY bytes; the server replays recent scrollback on attach,
    // so a reconnect redraws rather than showing a blank screen. That replay ends
    // at a {"replay":"end"} text frame — until then the stream is history, and its
    // control sequences must be drawn but not *acted on* (see `live` below).
    socket.onmessage = function (ev) {
      if (ev.data instanceof ArrayBuffer) { term.write(new Uint8Array(ev.data)); return; }
      if (typeof ev.data !== 'string') { return; }
      var msg;
      try { msg = JSON.parse(ev.data); } catch (e) { return; }
      if (!msg || msg.replay !== 'end') { return; }
      // term.write() is asynchronous — the replayed bytes are queued for parsing,
      // so flipping the flag here would still let the queue's OSC sequences through.
      // Queue the flip *behind* them instead: a write's callback runs once that
      // write is parsed, and NUL is the one byte the VT parser ignores outright, so
      // it draws nothing and lands exactly on the scrollback/live boundary. (It has
      // to be a real byte — xterm does not run the callback for an empty write.)
      term.write('\x00', function () { live = true; });
    };
    socket.onclose = function (ev) {
      disarm();
      socket = null;
      report(false);
      if (closedByUs) {
        term.write('\r\n\x1b[33mdisconnected — your shell keeps running; '
                   + 'reconnect from the user menu.\x1b[0m\r\n');
        return;
      }
      // 1008 = the service refused us (no ticket / not permitted): say so.
      if (ev.code === 1008) {
        term.write('\r\n\x1b[31m' + (ev.reason || 'shell refused') + '\x1b[0m\r\n');
        return;
      }
      // Anything else: the transport dropped. No automatic reconnect — say what
      // happened and leave the next move to the user (☰ → Connect terminal).
      term.write('\r\n\x1b[33mconnection lost — reconnect from the user menu '
                 + '(your shell keeps running).\x1b[0m\r\n');
    };
  }

  function send(data) {
    if (socket && socket.readyState === WebSocket.OPEN) { socket.send(data); }
  }

  function sendSize() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      send(JSON.stringify({ resize: [term.cols, term.rows] }));
    }
  }

  term.onData(function (data) { send(new TextEncoder().encode(data)); });
  term.onResize(sendSize);

  // The pane is a flex/grid cell; a window resize (or the shell's layout
  // settling) changes its box, and fit() recomputes cols/rows — which fires
  // onResize above, so the PTY follows the browser.
  var pending = null;
  function refit() {
    clearTimeout(pending);
    pending = setTimeout(function () { try { fit.fit(); } catch (e) { /* detached */ } }, 60);
  }
  window.addEventListener('resize', refit);
  new ResizeObserver(refit).observe(host);

  // ── OSC 5379: the shell drives the left pane (solver/core/viewer.py) ──────
  // `show` / `edit` in a web shell emit ESC ] 5379 ; <payload> BEL on the PTY:
  //   open;<NNNN>;<token>              → /solutions/NNNN/
  //   edit;<NNNN>;<token>;<relpath>    → /edit/solutions/NNNN/<relpath>
  //
  // Two guards, for two different re-runs of the same sequence:
  //   · `live` — the attach replay redraws commands that already ran. Acting on
  //     those would hijack the pane on every page load (a deep link to one problem
  //     would bounce to whatever the shell last showed). Drawn, never obeyed.
  //   · `lastToken` — the token is a server-side ms clock, strictly increasing per
  //     command, so a sequence we have already passed cannot navigate again.
  var lastToken = 0;
  term.parser.registerOscHandler(5379, function (payload) {
    var parts = payload.split(';');
    var action = parts[0], number = parts[1], token = Number(parts[2]) || 0;
    if (!live || !/^\d+$/.test(number || '') || token <= lastToken) { return true; }
    var path = null;
    if (action === 'open') {
      path = '/solutions/' + number + '/';
    } else if (action === 'edit') {
      var file = parts.slice(3).join(';');    // rejoin: a relpath may contain ';'
      if (file) { path = '/edit/solutions/' + number + '/' + file; }
    }
    if (path && window.parent !== window) {
      lastToken = token;
      // Framed (the normal case): the parent owns the left pane, and we ask it to
      // swap — never reaching into its DOM. Unframed (a direct visit to /terminal)
      // there is no pane to drive, so the sequence is simply consumed.
      window.parent.postMessage({ euler: 'navigate', path: path }, location.origin);
    }
    return true;                              // handled — not printable text
  });

  // ── clipboard ────────────────────────────────────────────────────────────
  // In a browser, Ctrl-C with a selection means "copy", not "interrupt"; Ctrl-V
  // must go through the clipboard API. Everything else falls through to the PTY
  // (so a bare Ctrl-C still interrupts the running command).
  term.attachCustomKeyEventHandler(function (ev) {
    if (ev.type !== 'keydown' || !ev.ctrlKey || ev.altKey || ev.metaKey) { return true; }
    var key = ev.key.toLowerCase();
    if (key === 'c' && term.hasSelection()) {
      navigator.clipboard && navigator.clipboard.writeText(term.getSelection());
      term.clearSelection();
      return false;
    }
    if (key === 'v') {
      // preventDefault, or the paste runs TWICE: returning false only skips
      // xterm's own key handling — the browser still performs its native paste
      // into xterm's hidden textarea (a second term.paste of the same text).
      // Cancelling the keydown suppresses that native paste; ours is the one.
      ev.preventDefault();
      navigator.clipboard && navigator.clipboard.readText().then(function (text) {
        if (text) { term.paste(text); }
      });
      return false;
    }
    return true;
  });

  // ── the refresh guard (web-server-guide § The site) ───────────────────────────────────
  // htmx navigation cannot reach this document, so only a *full* load — F5, the
  // address bar, closing the tab — can tear the terminal down. Ask first while a
  // session is live. The PTY itself survives server-side either way (one
  // persistent shell per user, replayed on reconnect); what the dialog protects
  // is the scrollback and whatever is mid-flow on screen.
  var guard = null;
  function beforeUnload(ev) { ev.preventDefault(); ev.returnValue = ''; return ''; }
  function arm() {
    if (!guard) { guard = beforeUnload; window.addEventListener('beforeunload', guard); }
  }
  function disarm() {
    if (guard) { window.removeEventListener('beforeunload', guard); guard = null; }
  }

  // Parent → here (site.js): the user-menu terminal controls, plus 'disarm'
  // before a deliberate exit (logout) so the beforeunload dialog stays quiet.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== location.origin || !ev.data) { return; }
    switch (ev.data.euler) {
      case 'disarm':                    // logout: the user's own choice, no dialog
        closedByUs = true;
        disarm();
        if (socket) { socket.close(1000, 'leaving'); }
        break;
      case 'disconnect':                // ☰ → Disconnect terminal
        closedByUs = true;
        if (socket) { socket.close(1000, 'user disconnect'); }
        break;
      case 'connect':                   // ☰ → Connect terminal (idempotent)
        if (!socket) {
          if (window.Vault) { window.Vault.unlock().then(connect, connect); }
          else { connect(); }
        }
        break;
    }
  });

  // Unlock the vault BEFORE the first attach: the shell is forked on
  // attach and inherits the session key file's path by environment, so the
  // unlock must land first for the shell (and the git filter under it) to
  // decrypt the user's secrets. Best-effort — locked just means `claude-api`
  // and the private solutions stay unavailable in this shell.
  if (window.Vault) {
    window.Vault.unlock().then(connect, connect);
  } else {
    connect();
  }
})();
