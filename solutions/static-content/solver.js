'use strict';

const statusEl = document.getElementById('status');

function setStatus(symbol, title, cls) {
    statusEl.textContent = symbol;
    statusEl.title = title;
    statusEl.className = cls || '';
}

const term = new Terminal({
    cursorBlink: true,
    fontFamily: 'monospace',
    fontSize: 14,
    theme: {background: '#1e1e1e'},
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

ws.onopen = () => {
    setStatus('●', 'connected', 'open');   // ● filled circle
    sendResize();          // prompt-toolkit/rich need the real geometry up front
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
    term.write('\r\n\x1b[2m[connection closed]\x1b[0m\r\n');
};

ws.onerror = () => setStatus('✕', 'connection error', 'error');   // ✕ cross

// Keystrokes from xterm → PTY input, as binary.
term.onData((data) => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(encoder.encode(data));
    }
});

window.addEventListener('resize', () => {
    fitAddon.fit();
    sendResize();
});

term.focus();