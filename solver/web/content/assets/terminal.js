/* The right pane's terminal (site-design §1/decision 14, DD-13/DD-14).

   Its own document, framed by the app shell at #ws, so htmx swaps, content-page
   JS, and history restores structurally cannot touch the session. It talks only
   to /ws — xterm.js in, raw PTY bytes out — and to its parent, by postMessage:

   - down (parent → here): {euler: 'disarm'} before a deliberate exit (logout),
     so the beforeunload guard does not fire on a navigation the user chose;
   - up (here → parent): {euler: 'navigate', path} when the shell's `show`/`edit`
     emits its OSC 5379 sequence — the shell drives the left pane, and only ever
     through the parent (this document never touches the parent's DOM).

   Wire protocol (solver/web/ws/app.py): binary frames are raw PTY bytes both
   ways; a text frame {"resize": [cols, rows]} carries the geometry. */
(function () {
  'use strict';

  var host = document.getElementById('term');
  if (!host || typeof window.Terminal !== 'function') { return; }

  // ── theme: the terminal is dark in both site themes ──────────────────────
  // Deliberate, and the one surface that does not follow the slider. What renders
  // here is the *shell's own* output, and the shell paints with absolute xterm-256
  // indices chosen for a dark terminal (near-whites like 254/247 for body text,
  // 238 for rules) — on a light background its banner and prompt wash out to
  // illegible. Re-theming the surface without re-tuning the shell's palette would
  // just break the contrast the shell already designed for. So: a dark terminal
  // panel on a light page, the way an embedded console normally reads. The tokens
  // are the site's own dark palette, so it is the same surface, not a foreign one.
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
  var socket = null;
  var closedByUs = false;
  var retry = 0;
  //: False while the server's replay is still being parsed: the scrollback is
  //: drawn, but the commands in it already ran, so their control sequences must
  //: not fire again (§ the OSC handler below).
  var live = false;

  function connect() {
    var url = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';
    socket = new WebSocket(url);
    socket.binaryType = 'arraybuffer';

    socket.onopen = function () {
      retry = 0;
      live = false;                     // a fresh attach replays before it streams
      arm();
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
      if (closedByUs) { return; }
      // 1008 = the service refused us (no ticket / not permitted): say so and
      // stop — retrying cannot help. Anything else is a transport blip.
      if (ev.code === 1008) {
        term.write('\r\n\x1b[31m' + (ev.reason || 'shell refused') + '\x1b[0m\r\n');
        return;
      }
      term.write('\r\n\x1b[33mdisconnected — reconnecting…\x1b[0m\r\n');
      retry = Math.min(retry + 1, 6);
      setTimeout(connect, Math.min(500 * Math.pow(2, retry - 1), 15000));
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
      navigator.clipboard && navigator.clipboard.readText().then(function (text) {
        if (text) { term.paste(text); }
      });
      return false;
    }
    return true;
  });

  // ── the refresh guard (site-design §9) ───────────────────────────────────
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

  // The shell posts {euler: 'disarm'} before a deliberate exit (logout): that is
  // the user's own choice, so no dialog — and we close the socket ourselves so
  // the reconnect loop does not fight the navigation.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== location.origin || !ev.data || ev.data.euler !== 'disarm') { return; }
    closedByUs = true;
    disarm();
    if (socket) { socket.close(1000, 'leaving'); }
  });

  // Unlock the vault BEFORE the first attach (MT-12): the shell is forked on
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
