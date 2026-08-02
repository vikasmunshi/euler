/* The right pane's terminal (web-server-guide § The site).

   Its own document, framed by the app shell at #ws, so htmx swaps, content-page
   JS, and history restores structurally cannot touch the session. It talks only
   to /ws — xterm.js in, raw PTY bytes out — and to its parent, by postMessage:

   - down (parent → here): {euler: 'disarm'} before a deliberate exit (logout),
     so the beforeunload guard does not fire on a navigation the user chose;
     {euler: 'connect'|'disconnect'} from the terminal titlebar's toggle;
     {euler: 'focus'} from a show control, which reveals the pane but cannot
     reach across this boundary to put the caret in the shell itself;
   - up (here → parent): {euler: 'navigate', path} when the shell's `show`/`edit`
     emits its OSC 5379 sequence — the shell drives the left pane, and only ever
     through the parent (this document never touches the parent's DOM);
     {euler: 'git-changed'} when a git command reports it moved this clone, so the
     header's chip re-reads itself;
     {euler: 'term-state', connected} whenever the socket opens or closes, so the
     titlebar's toggle can name the act it offers.

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
  // Connect and disconnect are the USER'S acts (the titlebar's toggle; the first
  // connect rides the page load). There is deliberately no automatic reconnect:
  // a dropped transport stays dropped, visibly, until the user asks — the
  // server-side shell survives a disconnect and replays on the next attach.
  var socket = null;
  var closedByUs = false;

  //: Tell the shell where we stand. The titlebar's toggle follows this and
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
      if (!msg) { return; }
      // A message landed for this user: euler-msg nudged this instance, which sent this
      // frame (solver/web/user/msg_api.py). It rides a TEXT frame, not the PTY, and so
      // is NOT in the replay buffer — no `live` guard and no token are needed, and it
      // cannot be mistaken for shell output. Tell the parent; the header's chip re-reads.
      if (msg.euler === 'message' && window.parent !== window) {
        window.parent.postMessage({ euler: 'message', unread: msg.unread }, location.origin);
        return;
      }
      if (msg.replay !== 'end') { return; }
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
                   + 'reconnect from the titlebar above.\x1b[0m\r\n');
        return;
      }
      // 1008 = the service refused us (no ticket / not permitted): say so.
      if (ev.code === 1008) {
        term.write('\r\n\x1b[31m' + (ev.reason || 'shell refused') + '\x1b[0m\r\n');
        return;
      }
      // Anything else: the transport dropped. No automatic reconnect — say what
      // happened and leave the next move to the user (the titlebar's Connect).
      term.write('\r\n\x1b[33mconnection lost — reconnect from the titlebar above '
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

  // ── OSC 5379: the shell drives the chrome (solver/core/osc.py) ────────────
  // A web shell emits ESC ] 5379 ; <payload> BEL on the PTY. The action is always
  // the first field; the token's position is per-action, because `edit` must keep
  // its relpath last (a path may contain ';', so only the last field can absorb it):
  //   open;<NNNN>;<token>              → swap the pane to /solutions/NNNN/
  //   edit;<NNNN>;<token>;<relpath>    → swap the pane to /edit/solutions/NNNN/<relpath>
  //   git;<token>                      → the header's git chip re-reads itself
  //   msg;<token>                      → the header's message chip re-reads itself
  //
  // Two guards, for two different re-runs of the same sequence:
  //   · `live` — the attach replay redraws commands that already ran. Acting on
  //     those would hijack the pane on every page load (a deep link to one problem
  //     would bounce to whatever the shell last showed). Drawn, never obeyed.
  //   · `lastToken` — the token is a server-side ms clock, strictly increasing per
  //     command, so a sequence we have already passed cannot fire again.
  var lastToken = 0;

  //: The message an OSC payload asks the parent to send, or null if it asks nothing.
  //: Pure: the guards and the postMessage live in the handler, so this stays a
  //: statement about the wire alone.
  function oscMessage(parts) {
    var action = parts[0];
    if (action === 'git') {
      return { euler: 'git-changed' };
    }
    // The same message the SERVER's delivery nudge posts (the text frame above), because
    // the page's answer is identical either way: re-read the chip. What differs is who
    // moved — someone else sending you mail, or you reading it in your own shell — and
    // the chip does not care.
    if (action === 'msg') {
      return { euler: 'message' };
    }
    if (action === 'account') {
      return { euler: 'account-changed' };
    }
    var number = parts[1];
    if (!/^\d+$/.test(number || '')) { return null; }
    if (action === 'open') {
      return { euler: 'navigate', path: '/solutions/' + number + '/' };
    }
    if (action === 'edit') {
      var file = parts.slice(3).join(';');    // rejoin: a relpath may contain ';'
      return file ? { euler: 'navigate', path: '/edit/solutions/' + number + '/' + file } : null;
    }
    return null;
  }

  //: Where the token sits: second field for the fieldless nudges (`git`, `msg`,
  //: `account`), third for the pane actions that carry a problem number first (§ above).
  function oscToken(parts) {
    var fieldless = parts[0] === 'git' || parts[0] === 'msg' || parts[0] === 'account';
    return Number(fieldless ? parts[1] : parts[2]) || 0;
  }

  term.parser.registerOscHandler(5379, function (payload) {
    var parts = payload.split(';');
    var token = oscToken(parts);
    if (!live || token <= lastToken) { return true; }
    var message = oscMessage(parts);
    if (message && window.parent !== window) {
      lastToken = token;
      // Framed (the normal case): the parent owns the pane and the header, and we
      // ask it to act — never reaching into its DOM. Unframed (a direct visit to
      // /terminal) there is no chrome to drive, so the sequence is simply consumed.
      window.parent.postMessage(message, location.origin);
    }
    return true;                              // handled — not printable text
  });

  // ── modified Enter (web-server-guide § 12.2) ──────────────────────────────
  // xterm.js sends Enter as a bare CR whatever else is held down — its keyboard
  // knows only Alt, as ESC CR — so Shift-Enter arrives at the PTY indistinguishable
  // from Enter, and the tools that read it as "newline, don't submit" (Claude Code)
  // never see it. Two encodings carry the modifier, and which one is right is the
  // *application's* to say, not ours:
  //
  //   kitty keyboard    CSI 13 ; <mod> u       on: CSI > <flags> u   off: CSI < u
  //   modifyOtherKeys   CSI 27 ; <mod> ; 13 ~  on: CSI > 4 ; <n> m   off: CSI > 4 m
  //
  // Neither may be sent unasked: a reader that knows only the legacy encoding takes
  // CSI 27;2;13~ for text and lands `;2;13~` in its line buffer — bash does exactly
  // that. So we follow what the foreground app turned on, and with nothing on fall
  // back to what a terminal user would have bound by hand (below).
  //
  // The mode state is rebuilt from the attach replay as well, deliberately, and
  // unlike the OSC actions below: an action must not re-fire, but a *mode* is the
  // state of the shell we are reattaching to, still running whatever app set it.
  // A truncated replay cannot leave us wrongly enabled — the buffer drops its
  // oldest bytes, so an enable is lost before, or along with, its disable.
  var kittyFlags = [0];                 // the kitty flag stack; [0] is the base entry
  var otherKeys = 0;                    // xterm's modifyOtherKeys level (0 = off)

  //: One CSI parameter as a plain integer. xterm hands sub-parameters (`38:2:…`)
  //: through as arrays and omitted ones as 0; no sequence read here uses either.
  function param(params, index, fallback) {
    var value = params[index];
    if (Array.isArray(value)) { value = value[0]; }
    return typeof value === 'number' ? value : fallback;
  }

  term.parser.registerCsiHandler({ prefix: '>', final: 'u' }, function (params) {
    kittyFlags.push(param(params, 0, 0));
    return true;
  });
  term.parser.registerCsiHandler({ prefix: '<', final: 'u' }, function (params) {
    var count = param(params, 0, 1) || 1;
    while (count-- > 0 && kittyFlags.length > 1) { kittyFlags.pop(); }
    return true;
  });
  term.parser.registerCsiHandler({ prefix: '=', final: 'u' }, function (params) {
    var flags = param(params, 0, 0);
    var mode = param(params, 1, 1) || 1;      // 1 = assign, 2 = set bits, 3 = clear bits
    var top = kittyFlags.length - 1;
    kittyFlags[top] = mode === 2 ? kittyFlags[top] | flags
      : mode === 3 ? kittyFlags[top] & ~flags
        : flags;
    return true;
  });
  // XTMODKEYS. Resource 4 is modifyOtherKeys; `CSI > m` carries no resource and
  // resets every one of them, which for us is the same answer: off.
  term.parser.registerCsiHandler({ prefix: '>', final: 'm' }, function (params) {
    var resource = param(params, 0, 0);
    if (resource === 0) { otherKeys = 0; }
    else if (resource === 4) { otherKeys = param(params, 1, 0); }
    return true;
  });
  // Not registered: the kitty query `CSI ? u`. Silence is the honest answer — we
  // encode Enter and nothing else, so advertising the flag set would promise an app
  // a disambiguated Esc and Tab it would then wait for. An app that enables the
  // protocol regardless (Claude Code does, for the terminals on its own allowlist)
  // is still obeyed above: what it turned on, it can read.

  //: The bytes for an Enter with modifiers held, or null when there is nothing to
  //: encode. The modifier number is the one both encodings share: 1, plus 1 shift,
  //: 2 alt, 4 ctrl.
  function enterSequence(ev) {
    var mod = 1 + (ev.shiftKey ? 1 : 0) + (ev.altKey ? 2 : 0) + (ev.ctrlKey ? 4 : 0);
    if (mod === 1) { return null; }                                   // bare Enter: xterm's CR
    if (kittyFlags[kittyFlags.length - 1] & 1) { return '\x1b[13;' + mod + 'u'; }
    if (otherKeys >= 1) { return '\x1b[27;' + mod + ';13~'; }
    // Nothing negotiated, so no encoding keeps the three apart and the question is
    // which byte each is most useful as. Ctrl-Enter takes LF — Ctrl-J's byte, and
    // "newline" to every reader that distinguishes one; Shift-Enter and Alt-Enter
    // take ESC CR, which is Meta-Enter to a readline-ish reader and is the binding
    // Claude Code's own /terminal-setup installs for this key in editors' terminals.
    return ev.ctrlKey && !ev.shiftKey && !ev.altKey ? '\n' : '\x1b\r';
  }

  // ── the keyboard ─────────────────────────────────────────────────────────
  // Enter with a modifier, per the section above; then the clipboard, because in a
  // browser Ctrl-C with a selection means "copy", not "interrupt", and Ctrl-V must
  // go through the clipboard API. Everything else falls through to the PTY (so a
  // bare Ctrl-C still interrupts the running command). Meta (Cmd / Win) is left
  // alone throughout — those chords are the browser's and the OS's.
  term.attachCustomKeyEventHandler(function (ev) {
    if (ev.type !== 'keydown' || ev.metaKey) { return true; }
    if (ev.key === 'Enter') {
      var sequence = enterSequence(ev);
      if (!sequence) { return true; }
      // preventDefault for the reason the paste below spells out: returning false
      // only skips xterm's own handling, and the key would still reach the hidden
      // textarea underneath — a second Enter, from the browser.
      ev.preventDefault();
      send(new TextEncoder().encode(sequence));
      return false;
    }
    if (!ev.ctrlKey || ev.altKey) { return true; }
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

  // Parent → here (site.js): the shell's terminal controls, plus 'disarm' before a
  // deliberate exit (logout) so the beforeunload dialog stays quiet.
  window.addEventListener('message', function (ev) {
    if (ev.origin !== location.origin || !ev.data) { return; }
    switch (ev.data.euler) {
      case 'disarm':                    // logout: the user's own choice, no dialog
        closedByUs = true;
        disarm();
        if (socket) { socket.close(1000, 'leaving'); }
        break;
      case 'disconnect':                // titlebar → Disconnect
        closedByUs = true;
        if (socket) { socket.close(1000, 'user disconnect'); }
        break;
      case 'connect':                   // titlebar → Connect (idempotent)
        if (!socket) {
          if (window.Vault) { window.Vault.unlock().then(connect, connect); }
          else { connect(); }
        }
        break;
      case 'focus':                     // a show control: put the caret in the shell
        // Focus is this document's to give — the parent cannot reach across the
        // iframe boundary to xterm's hidden textarea. Sent whether or not a socket
        // is up: an unfocused terminal is one the next keystroke misses, and
        // connecting is a separate act with its own control.
        term.focus();
        break;
      case 'run':                       // the account page's tool rows
        // Type the command and press return, exactly as the user would: it lands in
        // the shell's own readline, is echoed, and is theirs to edit or interrupt.
        // Nothing here is privileged — this is the same PTY the keyboard writes to.
        // With no session there is nothing to type into, and silently dropping it
        // would read as a dead button, so say so where the answer would have gone.
        if (typeof ev.data.command !== 'string' || !ev.data.command) { break; }
        if (socket && socket.readyState === WebSocket.OPEN) {
          term.focus();
          send(new TextEncoder().encode(ev.data.command + '\r'));
        } else {
          term.write('\r\n\x1b[33mconnect the terminal first, then try again.\x1b[0m\r\n');
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
