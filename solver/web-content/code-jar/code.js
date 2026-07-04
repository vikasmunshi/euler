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
// Only real source files can be deleted.
const DELETABLE = /\.(py|c)$/.test(FILENAME);

// Save / Delete and the filename / language badge live in the editor's own toolbar
// (code.html); Eval is a global action in the workspace command bar.
const BADGE = {python: 'PY', c: 'C', json: 'JSON', html: 'HTML'}[LANGUAGE] || (LANGUAGE || '').toUpperCase();
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

// ── Editor toolbar: Save / Delete + filename / language badge live locally in this
// page (code.html); Eval is global, in the workspace command bar.
const saveBtn = document.getElementById('save-btn');
const delBtn = document.getElementById('del-btn');

function fillMeta() {
    const fn = document.getElementById('filename');
    if (fn) fn.textContent = FILENAME;
    const badge = document.getElementById('lang-badge');
    if (badge && BADGE) { badge.hidden = false; badge.textContent = BADGE; }
}

// Ctrl/Cmd+S saves (CodeMirror's Mod-s keymap equivalent).
editorEl.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        save();
    }
});

// Show and enable the Save / Del buttons for an editable source file and make the
// editor writable. Generated / read-only views stay read-only.
function enableEditing() {
    if (!EDITABLE) return;
    saveBtn.hidden = false;
    saveBtn.disabled = false;
    saveBtn.title = 'Save (Ctrl/Cmd+S)';
    setEditable(true);
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

// Delete this solution file, then return to the problem view.
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
                window.location.href = `/${PROBLEM_NUMBER}/`;
            }, 800);  // file is gone; leave the editor for the problem view
            return;
        }
    } catch {
        showOutput('network error', 'error');
    }
    enableEditing();
}

// The toolbar buttons are in this page's own DOM, so wire them directly.
if (saveBtn) saveBtn.addEventListener('click', save);
if (delBtn) delBtn.addEventListener('click', runDelete);
fillMeta();
enableEditing();