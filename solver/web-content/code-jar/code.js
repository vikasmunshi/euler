import {CodeJar} from '/vendor/codejar.js';

const hljs = window.hljs;

// The page is served either read-only at /<n>/<filename> or as the editor at
// /edit/<n>/<filename>; drop the leading `edit` segment so the number/filename line up.
const RAW = window.location.pathname.split('/').filter(Boolean);
const EDIT_MODE = RAW[0] === 'edit';
const SEGMENTS = EDIT_MODE ? RAW.slice(1) : RAW;
const PROBLEM_NUMBER = SEGMENTS[0];
const FILENAME = SEGMENTS[SEGMENTS.length - 1];
const LANGUAGE = document.body.dataset.language;
// Editing is only offered on the /edit/ route; the read-only viewer never edits.
// Even there, only real solution files are editable (not the generated `solutions`
// view). HTML stubs (notes / statement) edit as plain text (no highlight.js
// language), but save verbatim.
const EDITABLE = EDIT_MODE && /\.(py|c|json|html)$/.test(FILENAME);
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

// CodeJar makes the element editable on init; editable source files are switched on
// once the header is ready. 'plaintext-only' keeps paste/Enter from injecting markup.
function setEditable(canEdit) {
    editorEl.setAttribute('contenteditable', canEdit ? 'plaintext-only' : 'false');
}

setEditable(false);  // read-only until the header wires up editing

// Clear stale command feedback as soon as the document changes.
jar.onUpdate(() => {
    renderGutter();
    if (!outputEl.hidden) showOutput('', '');
});

// ── Save / Eval / Delete: the buttons live in the shared header, so resolve them
// once header.js has injected it, then wire their handlers and enable editing.
let saveBtn, evalBtn, delBtn;

// Ctrl/Cmd+S saves (CodeMirror's Mod-s keymap equivalent).
editorEl.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        save();
    }
});

// Show and enable the Save / Eval / Delete buttons for an editable source file and
// make the editor writable. Generated views (e.g. `solutions`) stay read-only.
function enableEditing() {
    if (!EDITABLE) return;  // generated views stay read-only with no Save / Eval button
    saveBtn.hidden = false;
    saveBtn.disabled = false;
    saveBtn.title = 'Save (Ctrl/Cmd+S)';
    setEditable(true);
    if (EVALUABLE) {
        evalBtn.hidden = false;
        evalBtn.disabled = false;
        evalBtn.title = 'Evaluate this solution against its test cases';
    }
    if (DELETABLE) {
        delBtn.hidden = false;
        delBtn.disabled = false;
        delBtn.title = 'Delete this solution';
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
        enableEditing();  // re-enable the buttons
    }
}

// Dispatch `eval <n> lang=<lang> solution_index=<i>` (just this solution) to the
// user's web shell via /cmd; it runs there, output streaming to the terminal panel.
async function runEval() {
    if (evalBtn.disabled) return;
    evalBtn.disabled = true;
    const command = `eval ${PROBLEM_NUMBER} lang=${EVAL_MATCH[2]} solution_index=${parseInt(EVAL_MATCH[1], 10)}`;
    try {
        const r = await fetch('/cmd', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command}),
        });
        showOutput(r.ok ? `→ ${command} (running in the shell)` : 'dispatch failed', r.ok ? 'ok' : 'error');
    } catch {
        showOutput('network error', 'error');
    } finally {
        enableEditing();
    }
}

// Delete this solution file, then return to the problem page.
async function runDelete() {
    if (delBtn.disabled) return;
    if (!confirm(`Delete ${FILENAME}?`)) return;
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
    enableEditing();
}

// The header (with the buttons) is injected asynchronously; wire up once it is ready.
window.SolverHeader.ready.then(() => {
    saveBtn = document.getElementById('save-btn');
    evalBtn = document.getElementById('eval-btn');
    delBtn = document.getElementById('del-btn');
    saveBtn.addEventListener('click', save);
    evalBtn.addEventListener('click', runEval);
    delBtn.addEventListener('click', runDelete);
    enableEditing();
});