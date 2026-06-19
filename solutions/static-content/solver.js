'use strict';

const statusEl = document.getElementById('status');

function setStatus(symbol, title, cls) {
    statusEl.textContent = symbol;
    statusEl.title = title;
    statusEl.className = cls || '';
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

const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${wsProto}//${location.host}/ws`);
ws.binaryType = 'arraybuffer';

const encoder = new TextEncoder();
const decoder = new TextDecoder();

function sendResize() {
    if (ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({resize: [term.cols, term.rows]}));
}

function guardUnload(e) {
    e.preventDefault();
    e.returnValue = '';   // required for Chrome to show the prompt
}

ws.onopen = () => {
    setStatus('●', 'connected', 'open');   // ● filled circle
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
    setStatus('○', 'connection closed', 'error');   // ○ hollow circle
    window.removeEventListener('beforeunload', guardUnload);   // closed → nothing left to protect
    term.write('\r\n\x1b[2m[connection closed]\x1b[0m\r\n');
};

ws.onerror = () => setStatus('✕', 'connection error', 'error');   // ✕ cross

// Keystrokes from xterm → PTY input, as binary.
term.onData((data) => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(encoder.encode(data));
    }
});

// Swallow the F5 reload shortcut while connected, before the browser acts on
// it. Ctrl+R / ⌘-R are left alone so they reach the terminal (reverse-search).
// Does not cover the reload button — beforeunload does.
window.addEventListener('keydown', (e) => {
    if (e.key === 'F5' && ws.readyState === WebSocket.OPEN) {
        e.preventDefault();
        e.stopPropagation();
    }
}, true);

window.addEventListener('resize', () => {
    fitAddon.fit();
    sendResize();
});

term.focus();