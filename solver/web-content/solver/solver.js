'use strict';

// ── The workspace shell ──
// This page (`/`) owns the uniform command bar and the live terminal; the left
// content pane is an iframe onto the summary / problem / editor pages. The bar is
// independent of the iframe: it learns the current problem / file from the iframe
// via a `solver:ctx` postMessage (posted by header.js), and its glyph nav drives the
// iframe's `src`. The web `show` / `edit` commands navigate the iframe over the
// PTY → WebSocket pipe (OSC 5379). Eval dispatches a command to the shell via /cmd.

const content = document.getElementById('content');
const crumbEl = document.getElementById('crumb');
const evalBtn = document.getElementById('eval-btn');
const userBtn = document.getElementById('user-btn');
const userDropdown = document.getElementById('user-dropdown');
const connToggle = document.getElementById('conn-toggle');

const pad4 = (n) => String(n).padStart(4, '0');
const escapeHtml = (s) => s.replace(/[&<>"]/g, (c) => (
    {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

// ── Command bar: context + navigation ──
// `ctx` mirrors whatever the iframe currently shows; `activeProblem` is the shell's
// own variables.problem (from the server), where the ◇ link jumps from any page.
let ctx = {problem: 0, filename: '', label: ''};
let activeProblem = 0;

function navigate(path) { content.src = path; }

// Turn an internal glyph into a live link that drives the iframe, or an inert dummy.
function setInternal(el, path) {
    if (path) {
        el.dataset.nav = path;
        el.classList.remove('nav-dummy');
    } else {
        delete el.dataset.nav;
        el.classList.add('nav-dummy');
    }
}

// External links (Euler / GitHub) always have a target — a specific problem or the
// site root off a problem.
function setExternal(el, href) {
    el.href = href;
    el.classList.remove('nav-dummy');
}

function applyContext() {
    const n = ctx.problem;
    const onProblem = n > 0;
    if (onProblem) {
        let html = `<b>${n}</b>`;
        if (ctx.filename) html += ` &middot; editing ${escapeHtml(ctx.filename)}`;
        crumbEl.innerHTML = html;
    } else {
        crumbEl.textContent = ctx.label || '';
    }
    setInternal(document.getElementById('nav-prev'), onProblem && n > 1 ? `/${pad4(n - 1)}/` : null);
    setInternal(document.getElementById('nav-next'), onProblem ? `/${pad4(n + 1)}/` : null);
    setExternal(document.getElementById('nav-euler'),
        onProblem ? `https://projecteuler.net/problem=${n}` : 'https://projecteuler.net/progress');
    setExternal(document.getElementById('nav-github'),
        onProblem ? `https://github.com/vikasmunshi/euler/blob/master/solutions/${pad4(n).split('').join('/')}/`
            : 'https://github.com/vikasmunshi/euler');
    evalBtn.hidden = !onProblem;
}

// The active-problem jump (◇) tracks the shell's variables.problem from the server,
// so it points at the current problem from any page (not the browser URL).
async function refreshActiveProblem() {
    try {
        const r = await fetch('/active-problem', {headers: {Accept: 'application/json'}});
        if (!r.ok) return;
        const {problem} = await r.json();
        if (/^\d+$/.test(String(problem))) {
            activeProblem = Number(problem);
            setInternal(document.getElementById('nav-active'), `/${pad4(activeProblem)}/`);
        }
    } catch { /* leave the ◇ link inert */ }
}

// The iframe (via header.js) reports what it is showing; the bar reflects it.
window.addEventListener('message', (e) => {
    if (e.origin !== location.origin) return;
    const d = e.data;
    if (!d || d.type !== 'solver:ctx') return;
    ctx = {problem: Number(d.problem) || 0, filename: d.filename || '', label: d.label || ''};
    applyContext();
});

// Fixed internal targets + click delegation for every glyph that drives the iframe.
setInternal(document.getElementById('nav-summary'), '/summary');
setInternal(document.getElementById('nav-progress'), '/progress');
document.getElementById('nav').addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (a && a.dataset.nav) { e.preventDefault(); navigate(a.dataset.nav); }
});
applyContext();
refreshActiveProblem();

// Eval → dispatch `eval <n>` to the user's shell (the terminal shows the run). Uses
// /cmd so it works regardless of this page's socket state.
evalBtn.addEventListener('click', () => {
    if (ctx.problem > 0) {
        fetch('/cmd', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: `eval ${ctx.problem}`}),
        }).catch(() => { /* ignore: the shell is the source of truth */ });
    }
});

// ── Terminal (right pane) ──
function setConnState(state) {
    const connected = state === 'connected';
    const busy = connected || state === 'connecting';
    userBtn.className = 'user-btn ' + (connected ? 'connected' : (busy ? '' : 'disconnected'));
    userBtn.title = state;
    connToggle.textContent = busy ? 'Disconnect' : 'Connect';
}

// Build the xterm theme from the CSS variables the active solver-theme.css defines,
// so swapping the theme symlink re-themes the terminal grid too.
function cssTheme() {
    const css = getComputedStyle(document.documentElement);
    const v = (name) => css.getPropertyValue(name).trim();
    return {
        background: v('--term-bg'), foreground: v('--term-fg'),
        cursor: v('--term-cursor'), cursorAccent: v('--term-cursor-accent'),
        selectionBackground: v('--term-selection'),
        black: v('--ansi-black'), red: v('--ansi-red'), green: v('--ansi-green'),
        yellow: v('--ansi-yellow'), blue: v('--ansi-blue'), magenta: v('--ansi-magenta'),
        cyan: v('--ansi-cyan'), white: v('--ansi-white'),
        brightBlack: v('--ansi-bright-black'), brightRed: v('--ansi-bright-red'),
        brightGreen: v('--ansi-bright-green'), brightYellow: v('--ansi-bright-yellow'),
        brightBlue: v('--ansi-bright-blue'), brightMagenta: v('--ansi-bright-magenta'),
        brightCyan: v('--ansi-bright-cyan'), brightWhite: v('--ansi-bright-white'),
    };
}

const term = new Terminal({
    cursorBlink: true,
    fontFamily: 'monospace',
    fontSize: 14,
    // A small lineHeight bump gives the underscore descender room (else a typed '_'
    // is clipped to the cell's bottom pixel row and renders blank).
    lineHeight: 1.1,
    theme: cssTheme(),
    scrollback: 5000,
});
const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();

// ── Content navigation over the PTY pipe ──
// The web `show` / `edit` commands emit an OSC 5379 sequence on the shell's stdout —
// `open;<NNNN>;<token>` (show) or `edit;<NNNN>;<token>;<relpath>` (edit) — which rides
// the PTY → WebSocket pipe into term.write() here. We point the content iframe at the
// matching URL: `/<NNNN>/` for show, `/edit/<NNNN>/<relpath>` for edit. The token is a
// server-side millisecond clock, strictly increasing per command; we ignore any token
// we've already passed, so the copy the PTY replay buffer re-sends on reconnect never
// re-navigates the pane.
let lastViewerToken = 0;
term.parser.registerOscHandler(5379, (payload) => {
    const [action, n, token, ...rest] = payload.split(';');
    const t = Number(token) || 0;
    if (!/^\d+$/.test(n || '') || t <= lastViewerToken) return true;
    if (action === 'open') {
        lastViewerToken = t;
        navigate(`/${n}/`);
    } else if (action === 'edit') {
        const file = rest.join(';');   // rejoin so a relpath with a ';' survives the split
        if (file) { lastViewerToken = t; navigate(`/edit/${n}/${file}`); }
    }
    return true;   // handled — don't let xterm treat it as printable text
});

// In a browser, Ctrl-C with text selected is "copy", not "interrupt". Intercept it
// before xterm turns it into a ^C byte; likewise route Ctrl-V through the clipboard API.
term.attachCustomKeyEventHandler((e) => {
    if (e.type === 'keydown' && e.ctrlKey && !e.altKey && !e.metaKey && (e.key === 'c' || e.key === 'C')) {
        const sel = term.getSelection();
        if (sel) { navigator.clipboard?.writeText(sel); term.clearSelection(); return false; }
    }
    if (e.type === 'keydown' && e.ctrlKey && !e.altKey && !e.metaKey && (e.key === 'v' || e.key === 'V')) {
        navigator.clipboard?.readText().then((text) => { if (text) term.paste(text); });
        return false;
    }
    return true;
});
if (term.textarea) {
    term.textarea.addEventListener('paste', (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
    }, true);
}

// Bounce to login if the session has ended (e.g. this page came from the browser
// cache after logout); the /ws upgrade below would otherwise just fail.
fetch('/whoami', {cache: 'no-store', headers: {Accept: 'application/json'}})
    .then((r) => { if (!r.ok) window.location.replace('/login'); });

const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
const encoder = new TextEncoder();
let ws = null;

const isLive = () => ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING);

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
        window.addEventListener('beforeunload', guardUnload);
    };
    ws.onmessage = (ev) => {
        if (typeof ev.data === 'string') term.write(ev.data);
        else term.write(new Uint8Array(ev.data));
    };
    ws.onclose = () => {
        setConnState('disconnected');
        window.removeEventListener('beforeunload', guardUnload);
        term.write('\r\n\x1b[2m[connection closed]\x1b[0m\r\n');
    };
    ws.onerror = () => setConnState('error');
}

function disconnect() {
    window.removeEventListener('beforeunload', guardUnload);
    if (ws) ws.close();
}

term.onData((data) => {
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(encoder.encode(data));
});

// Swallow F5 (reload) while connected; Ctrl+R / ⌘-R reach the terminal (reverse-search).
window.addEventListener('keydown', (e) => {
    if (e.key === 'F5' && ws && ws.readyState === WebSocket.OPEN) {
        e.preventDefault();
        e.stopPropagation();
    }
}, true);

window.addEventListener('resize', () => { fitAddon.fit(); sendResize(); });

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
// A deliberate menu navigation (log out / change password) shouldn't trip the
// unsaved-session warning.
userDropdown.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => window.removeEventListener('beforeunload', guardUnload));
});

connect();
term.focus();
