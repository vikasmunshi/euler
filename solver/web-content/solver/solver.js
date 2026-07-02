'use strict';

const userBtn = document.getElementById('user-btn');
const userDropdown = document.getElementById('user-dropdown');
const connToggle = document.getElementById('conn-toggle');

// Reflect the WebSocket state in the account icon colour and the menu's
// Connect/Disconnect item ('connecting' | 'connected' | 'disconnected' | 'error').
function setConnState(state) {
    const connected = state === 'connected';
    const busy = connected || state === 'connecting';
    userBtn.className = 'user-btn ' + (connected ? 'connected' : (busy ? '' : 'disconnected'));
    userBtn.title = state;
    connToggle.textContent = busy ? 'Disconnect' : 'Connect';
}

// Build the xterm theme from the CSS variables the active solver-theme.css
// defines, so swapping the theme symlink re-themes the terminal grid too.
function cssTheme() {
    const css = getComputedStyle(document.documentElement);
    const v = (name) => css.getPropertyValue(name).trim();
    return {
        background: v('--term-bg'),
        foreground: v('--term-fg'),
        cursor: v('--term-cursor'),
        cursorAccent: v('--term-cursor-accent'),
        selectionBackground: v('--term-selection'),
        black: v('--ansi-black'),
        red: v('--ansi-red'),
        green: v('--ansi-green'),
        yellow: v('--ansi-yellow'),
        blue: v('--ansi-blue'),
        magenta: v('--ansi-magenta'),
        cyan: v('--ansi-cyan'),
        white: v('--ansi-white'),
        brightBlack: v('--ansi-bright-black'),
        brightRed: v('--ansi-bright-red'),
        brightGreen: v('--ansi-bright-green'),
        brightYellow: v('--ansi-bright-yellow'),
        brightBlue: v('--ansi-bright-blue'),
        brightMagenta: v('--ansi-bright-magenta'),
        brightCyan: v('--ansi-bright-cyan'),
        brightWhite: v('--ansi-bright-white'),
    };
}

const term = new Terminal({
    cursorBlink: true,
    fontFamily: 'monospace',
    fontSize: 14,
    // The DOM renderer clips each glyph to the cell height; at the default
    // lineHeight (1) the underscore sits on the bottom pixel row and is cut
    // off, so a typed/echoed '_' renders as blank background. A small bump
    // gives the descender room to show.
    lineHeight: 1.1,
    theme: cssTheme(),
    scrollback: 5000,
});
const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();

// In a browser, Ctrl-C with text selected is "copy", not "interrupt". Intercept
// it before xterm turns it into a ^C byte: when there is a selection, copy it to
// the clipboard and clear it; otherwise let the key through so it still sends
// SIGINT to the shell. (Only act on keydown — keypress/keyup would double-fire.)
term.attachCustomKeyEventHandler((e) => {
    if (e.type === 'keydown' && e.ctrlKey && !e.altKey && !e.metaKey &&
        (e.key === 'c' || e.key === 'C')) {
        const sel = term.getSelection();
        if (sel) {
            navigator.clipboard?.writeText(sel);
            term.clearSelection();
            return false;   // swallow: don't send ^C to the PTY
        }
    }
    // Ctrl-V → paste. We always do it ourselves via the clipboard API (below),
    // so swallow the key here to stop xterm's own keydown→paste path.
    if (e.type === 'keydown' && e.ctrlKey && !e.altKey && !e.metaKey &&
        (e.key === 'v' || e.key === 'V')) {
        navigator.clipboard?.readText().then((text) => {
            if (text) term.paste(text);
        });
        return false;
    }
    return true;
});

// Whichever browser/xterm build, a native `paste` event may still fire on the
// hidden textarea and trigger xterm's built-in paste. Suppress it in the capture
// phase so our clipboard-API path above is the single source of one paste.
if (term.textarea) {
    term.textarea.addEventListener('paste', (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
    }, true);
}

// Bounce to the login screen if the session has ended (e.g. this page came from the
// browser cache after logout); the /ws upgrade below would otherwise just fail.
fetch('/whoami', { cache: 'no-store', headers: { Accept: 'application/json' } })
    .then((r) => { if (!r.ok) window.location.replace('/login'); });

const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
const encoder = new TextEncoder();

let ws = null;

function isLive() {
    return ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING);
}

function sendResize() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({resize: [term.cols, term.rows]}));
    }
}

function guardUnload(e) {
    e.preventDefault();
    e.returnValue = '';   // required for Chrome to show the prompt
}

function connect() {
    if (isLive()) return;
    setConnState('connecting');
    ws = new WebSocket(`${wsProto}//${location.host}/ws`);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
        setConnState('connected');
        sendResize();          // prompt-toolkit/rich need the real geometry up front
        window.addEventListener('beforeunload', guardUnload);   // warn before any reload/navigation
    };
    // Binary frames are raw terminal bytes; write them straight to xterm.
    ws.onmessage = (ev) => {
        if (typeof ev.data === 'string') {
            term.write(ev.data);
        } else {
            term.write(new Uint8Array(ev.data));
        }
    };
    ws.onclose = () => {
        setConnState('disconnected');
        window.removeEventListener('beforeunload', guardUnload);   // closed → nothing left to protect
        term.write('\r\n\x1b[2m[connection closed]\x1b[0m\r\n');
    };
    ws.onerror = () => setConnState('error');
}

function disconnect() {
    window.removeEventListener('beforeunload', guardUnload);
    if (ws) ws.close();
}

// Keystrokes from xterm → PTY input, as binary.
term.onData((data) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(encoder.encode(data));
    }
});

// Swallow the F5 reload shortcut while connected, before the browser acts on
// it. Ctrl+R / ⌘-R are left alone so they reach the terminal (reverse-search).
// Does not cover the reload button — beforeunload does.
window.addEventListener('keydown', (e) => {
    if (e.key === 'F5' && ws && ws.readyState === WebSocket.OPEN) {
        e.preventDefault();
        e.stopPropagation();
    }
}, true);

window.addEventListener('resize', () => {
    fitAddon.fit();
    sendResize();
});

// Account menu: toggle on click, close on an outside click.
userBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const opening = userDropdown.hidden;
    userDropdown.hidden = !opening;
    userBtn.setAttribute('aria-expanded', String(opening));
});
document.addEventListener('click', () => {
    if (!userDropdown.hidden) {
        userDropdown.hidden = true;
        userBtn.setAttribute('aria-expanded', 'false');
    }
});
connToggle.addEventListener('click', () => (isLive() ? disconnect() : connect()));
// A deliberate navigation from the menu (log out / change password) should not
// trigger the unsaved-session warning.
userDropdown.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => window.removeEventListener('beforeunload', guardUnload));
});

connect();
term.focus();