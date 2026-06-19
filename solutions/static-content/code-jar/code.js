import {CodeJar} from '/vendor/codejar.js';

const hljs = window.hljs;

// Problem number and filename come from the URL: /<n>/<filename>.
const SEGMENTS = window.location.pathname.split('/').filter(Boolean);
const PROBLEM_NUMBER = SEGMENTS[0];
const FILENAME = SEGMENTS[SEGMENTS.length - 1];
const LANGUAGE = document.body.dataset.language;
// Only real solution files are editable; generated views (flags, solutions) are not.
const EDITABLE = /\.(py|c|json)$/.test(FILENAME);
// Source files can be evaluated / deleted; derive (lang, index) from p<NNNN>_s<K>.<ext>.
const EVAL_MATCH = FILENAME.match(/_s(\d+)\.(py|c)$/);
const EVALUABLE = EVAL_MATCH !== null;
const DELETABLE = /\.(py|c)$/.test(FILENAME);

// The nav bar, filename, and language badge are drawn by the shared header.js;
// the Eval/Save/Del buttons live in that header too, wired up below once it loads.
const outputEl = document.getElementById('save-output');

// All command feedback (result line + captured output) goes to the output panel;
// kind ('ok' | 'error' | '') tints it.
function showOutput(text, kind) {
    outputEl.textContent = text;
    outputEl.className = kind ? `output-${kind}` : '';
    outputEl.hidden = !text;
}

// highlight.js language id for the file's language (empty for generated views).
const HL_LANG = {python: 'python', c: 'c', json: 'json'}[LANGUAGE] || '';

// CodeJar's highlight callback: repaint the editor's innerHTML from its text.
function highlight(editorEl) {
    const code = editorEl.textContent;
    editorEl.innerHTML = HL_LANG
        ? hljs.highlight(code, {language: HL_LANG, ignoreIllegals: true}).value
        : code.replace(/[&<>]/g, ch => ({'&': '&amp;', '<': '&lt;', '>': '&gt;'}[ch]));
}

const editorEl = document.getElementById('editor');
const jar = CodeJar(editorEl, highlight, {tab: '    ', catchTab: true, spellcheck: false});

// Line-number gutter: one number per text line (no wrapping, so rows map 1:1).
// Repaint on every edit and keep its vertical scroll locked to the editor's.
const gutterEl = document.getElementById('gutter');
function renderGutter() {
    const lines = jar.toString().split('\n').length;
    let text = '';
    for (let i = 1; i <= lines; i++) text += `${i}\n`;
    gutterEl.textContent = text;
}
editorEl.addEventListener('scroll', () => {
    gutterEl.scrollTop = editorEl.scrollTop;
});

jar.updateCode(document.getElementById('source').value);
renderGutter();

// CodeJar makes the element editable on init; gate that on /flags like before.
// 'plaintext-only' keeps paste/Enter from injecting markup into the source.
function setEditable(canEdit) {
    editorEl.setAttribute('contenteditable', canEdit ? 'plaintext-only' : 'false');
}

setEditable(false);  // read-only until /flags confirms we may save

// Clear stale command feedback as soon as the document changes.
jar.onUpdate(() => {
    renderGutter();
    if (!outputEl.hidden) showOutput('', '');
});

// ── Save / Eval / Delete: the buttons live in the shared header, so resolve them
// once header.js has injected it, then wire their handlers and the first flag check.
let saveBtn, evalBtn, delBtn;

// Ctrl/Cmd+S saves (CodeMirror's Mod-s keymap equivalent).
editorEl.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        save();
    }
});

async function refreshFlags() {
    if (!EDITABLE) return;  // generated views stay read-only with no Save / Eval button
    let flags = {};
    try {
        const r = await fetch(`/flags?problem_number=${PROBLEM_NUMBER}`, {headers: {Accept: 'application/json'}});
        if (r.ok) flags = await r.json();
    } catch { /* server unreachable: stay read-only */
    }
    // Editing / evaluating the workspace needs an authoritative server with this problem active.
    const canSave = !!(flags.authoritative && flags.active);
    saveBtn.hidden = false;
    saveBtn.disabled = !canSave;
    saveBtn.title = canSave ? 'Save to workspace (Ctrl/Cmd+S)' : 'Workspace is read-only here';
    setEditable(canSave);
    if (EVALUABLE) {
        evalBtn.hidden = false;
        evalBtn.disabled = !canSave;
        evalBtn.title = canSave ? 'Evaluate this solution against its test cases'
            : 'Workspace is read-only here';
    }
    if (DELETABLE) {
        delBtn.hidden = false;
        delBtn.disabled = !canSave;
        delBtn.title = canSave ? 'Delete this solution from the workspace'
            : 'Workspace is read-only here';
    }
}

async function save() {
    if (!saveBtn || saveBtn.disabled) return;
    saveBtn.disabled = true;
    showOutput('saving…', '');
    try {
        const r = await fetch(window.location.pathname, {
            method: 'POST',
            headers: {'Content-Type': 'text/plain; charset=utf-8'},
            body: jar.toString(),
        });
        const message = await r.text();
        showOutput(message || (r.ok ? 'saved' : 'save failed'), r.ok ? 'ok' : 'error');
    } catch {
        showOutput('network error', 'error');
    } finally {
        await refreshFlags();  // re-enable only if the workspace is still writable
    }
}

// Evaluate just this solution (its language + index) via the /<n>/eval endpoint.
async function runEval() {
    if (evalBtn.disabled) return;
    evalBtn.disabled = true;
    showOutput('evaluating…', '');
    try {
        const r = await fetch(`/${PROBLEM_NUMBER}/cmd`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                cmd: 'eval',
                lang: EVAL_MATCH[2],
                solution_index: parseInt(EVAL_MATCH[1], 10),
            }),
        });
        const res = await r.json().catch(() => ({}));
        showOutput(res.output || (r.ok ? 'eval ok' : 'eval failed'), r.ok ? 'ok' : 'error');
    } catch {
        showOutput('network error', 'error');
    } finally {
        await refreshFlags();
    }
}

// Delete this solution file from the workspace, then return to the problem page.
async function runDelete() {
    if (delBtn.disabled) return;
    if (!confirm(`Delete
    ${FILENAME} from the workspace?`)) return;
    delBtn.disabled = true;
    showOutput('deleting…', '');
    try {
        const r = await fetch(window.location.pathname, {method: 'DELETE'});
        const message = await r.text();
        showOutput(message || (r.ok ? 'deleted' : 'delete failed'), r.ok ? 'ok' : 'error');
        if (r.ok) {
            setTimeout(() => {
                window.location.href = './';
            }, 800);  // file is gone; leave the editor
            return;
        }
    } catch {
        showOutput('network error', 'error');
    }
    await refreshFlags();
}

// The header (with the buttons) is injected asynchronously; wire up once it is ready.
window.SolverHeader.ready.then(() => {
    saveBtn = document.getElementById('save-btn');
    evalBtn = document.getElementById('eval-btn');
    delBtn = document.getElementById('del-btn');
    saveBtn.addEventListener('click', save);
    evalBtn.addEventListener('click', runEval);
    delBtn.addEventListener('click', runDelete);
    refreshFlags();
});