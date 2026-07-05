'use strict';

// ── The workspace shell ──
// This page (`/`) owns the uniform command bar and the live terminal; the left
// content pane is an iframe onto the summary / problem / editor pages. The bar is
// independent of the iframe: it learns the current problem / file from the iframe
// via a `solver:ctx` postMessage (posted by header.js), and its glyph nav drives the
// iframe's `src`. The web `show` / `edit` commands navigate the iframe over the
// PTY → WebSocket pipe (OSC 5379). Eval dispatches a command to the shell via /cmd.

const content = document.getElementById('content');
const breadcrumbEl = document.getElementById('breadcrumb');
const benchBtn = document.getElementById('bench-btn');
const evalBtn = document.getElementById('eval-btn');
const showBtn = document.getElementById('show-btn');
const userBtn = document.getElementById('user-btn');
const userDropdown = document.getElementById('user-dropdown');
const connToggle = document.getElementById('conn-toggle');

const pad4 = (n) => String(n).padStart(4, '0');
const escapeHtml = (s) => s.replace(/[&<>"]/g, (c) => (
    {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

// ── Command bar: context + navigation ──
// `ctx` mirrors whatever the iframe currently shows. The problem jumps (prev/active/
// next) run `show` in the shell so its current problem tracks the view (see showInShell).
let ctx = {problem: 0, filename: '', label: ''};

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

// The breadcrumb trail (root → current) for the content pane's context. Each segment
// is {text, href?}; one with an href navigates the pane, the trailing current leaf has
// none. The brand (home → /index) is the implicit root before the trail.
function buildTrail() {
    const {path, problem, filename, label} = ctx;
    if (problem > 0) {
        const trail = [{text: 'problems', href: '/summary'}];
        if (filename) {
            trail.push({text: String(problem), href: `/${pad4(problem)}/`});
            trail.push({text: filename});
        } else {
            trail.push({text: String(problem)});
        }
        return trail;
    }
    if (path && (path.startsWith('/docs/') || path.startsWith('/ai/'))) {
        return [{text: 'guides', href: '/index'}, {text: label}];
    }
    if (path === '/edit/progress') return [{text: 'problems', href: '/summary'}, {text: 'progress'}];
    if (path === '/index') return [{text: 'guides'}];
    if (path === '/summary') return [{text: 'problems'}];
    return label ? [{text: label}] : [];
}

function renderBreadcrumb() {
    breadcrumbEl.innerHTML = buildTrail().map((s) => {
        const seg = s.href
            ? `<a class="bc-seg" data-nav="${s.href}">${escapeHtml(s.text)}</a>`
            : `<span class="bc-seg bc-current">${escapeHtml(s.text)}</span>`;
        return `<span class="bc-sep">/</span>${seg}`;
    }).join('');
}

// The GitHub URL for a problem's solution directory: public/pNNNN for the plaintext
// problems (≤ 100), or the century-bucketed private/pXXXX_YYYY/pNNNN for the rest.
function githubUrl(n) {
    const base = 'https://github.com/vikasmunshi/euler/tree/master/solutions';
    if (n <= 100) return `${base}/public/p${pad4(n)}`;
    const bucket = Math.floor(n / 100) * 100;
    return `${base}/private/p${pad4(bucket)}_${pad4(bucket + 99)}/p${pad4(n)}`;
}

function applyContext() {
    const n = ctx.problem;
    const onProblem = n > 0;
    renderBreadcrumb();
    // prev / active / next run `show` in the shell (wired below) instead of navigating
    // the iframe directly, so they carry no data-nav here — only their inert/live state.
    document.getElementById('nav-prev').classList.toggle('nav-dummy', !(onProblem && n > 1));
    document.getElementById('nav-next').classList.toggle('nav-dummy', !onProblem);
    setExternal(document.getElementById('nav-euler'),
        onProblem ? `https://projecteuler.net/problem=${n}` : 'https://projecteuler.net/progress');
    setExternal(document.getElementById('nav-github'),
        onProblem ? githubUrl(n) : 'https://github.com/vikasmunshi/euler');
}

// The iframe (via header.js) reports what it is showing; the bar reflects it.
window.addEventListener('message', (e) => {
    if (e.origin !== location.origin) return;
    const d = e.data;
    if (!d || d.type !== 'solver:ctx') return;
    ctx = {path: d.path || '', problem: Number(d.problem) || 0, filename: d.filename || '', label: d.label || ''};
    applyContext();
});

// One delegated handler: anything in the bar carrying data-nav navigates the content
// pane directly — the brand (home), the breadcrumb segments, and the fixed section
// jumps. Euler/GitHub keep their real href (they open a new tab); the problem jumps
// (prev/active/next) go through the shell instead, below.
document.getElementById('cmdbar').addEventListener('click', (e) => {
    const el = e.target.closest('[data-nav]');
    if (el) { e.preventDefault(); navigate(el.getAttribute('data-nav')); }
});
// Fixed section jumps — always available.
setInternal(document.getElementById('nav-index'), '/index');
setInternal(document.getElementById('nav-summary'), '/summary');
setInternal(document.getElementById('nav-progress'), '/edit/progress');

// prev / active / next run `show` in the shell rather than navigating the iframe
// directly, so the console's current problem (variables.problem) stays in sync with
// the view: the shell's `show` sets the current problem and emits the OSC that moves
// the content pane. prev/next step from the viewed problem; the ◇ active jump shows
// the shell's own current problem (`show` with no argument).
function showInShell(arg) {
    fetch('/cmd', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: arg === '' ? 'show' : `show ${arg}`}),
    }).catch(() => { /* the shell is the source of truth */ });
}
document.getElementById('nav-prev').addEventListener('click', (e) => {
    e.preventDefault();
    if (ctx.problem > 1) showInShell(ctx.problem - 1);
});
document.getElementById('nav-next').addEventListener('click', (e) => {
    e.preventDefault();
    if (ctx.problem > 0) showInShell(ctx.problem + 1);
});
document.getElementById('nav-active').addEventListener('click', (e) => { e.preventDefault(); showInShell(''); });
applyContext();

// Command-bar action buttons. Each dispatches a SolverShell command to the user's shell
// via /cmd (so it works regardless of this page's socket state); the terminal shows the
// run. A command targets the problem currently in view, or the shell's own current
// problem when none is shown. The map key is the canonical command name (as in
// commands.csv), used both to dispatch and to check authorization below.
const barCommands = [
    {btn: benchBtn, cmd: 'benchmark'},
    {btn: evalBtn, cmd: 'evaluate'},
    {btn: showBtn, cmd: 'show'},
];

function dispatchCmd(cmd) {
    const line = ctx.problem > 0 ? `${cmd} ${ctx.problem}` : cmd;
    fetch('/cmd', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: line}),
    }).catch(() => { /* ignore: the shell is the source of truth */ });
}
barCommands.forEach(({btn, cmd}) => btn.addEventListener('click', () => dispatchCmd(cmd)));

// Visibility follows the signed-in user's *profile* (command authorization), fixed for
// the session — not the viewer's content. Ask the server which of these commands this
// profile may run; leave a button hidden if it may not (or the check fails).
const authzQuery = barCommands.map(({cmd}) => `cmd=${encodeURIComponent(cmd)}`).join('&');
fetch(`/authz?${authzQuery}`, {cache: 'no-store', headers: {Accept: 'application/json'}})
    .then((r) => (r.ok ? r.json() : {}))
    .then((allowed) => barCommands.forEach(({btn, cmd}) => { btn.hidden = !allowed[cmd]; }))
    .catch(() => { /* leave the buttons hidden */ });

// ── Terminal (right pane) ──
// The account button reflects the live connection state; its tooltip pairs that state
// with the signed-in user's email (filled in once /whoami resolves, below).
let userEmail = '';
let connState = 'connecting';

function renderUserBtn() {
    const connected = connState === 'connected';
    const busy = connected || connState === 'connecting';
    userBtn.className = 'user-btn ' + (connected ? 'connected' : (busy ? '' : 'disconnected'));
    userBtn.title = userEmail ? `${userEmail} ${connState}` : connState;
    connToggle.textContent = busy ? 'Disconnect' : 'Connect';
}

function setConnState(state) {
    connState = state;
    renderUserBtn();
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
    .then((r) => {
        if (!r.ok) { window.location.replace('/login'); return null; }
        return r.json();
    })
    .then((who) => { if (who) { userEmail = who.email || ''; renderUserBtn(); } })
    .catch(() => { /* transient network error; the tooltip just omits the email */ });

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
