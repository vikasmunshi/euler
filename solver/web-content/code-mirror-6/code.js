import {
    EditorView, basicSetup, EditorState, Compartment,
    keymap, indentWithTab, indentUnit, linter, lintGutter, forceLinting,
    python, cpp, json,
} from '/vendor/codemirror/cm6.js';

// The page is served either read-only at /<n>/<filename> or as the editor at
// /edit/<n>/<filename>; drop the leading `edit` segment so the number/filename line up.
const RAW = window.location.pathname.split('/').filter(Boolean);
const EDIT_MODE = RAW[0] === 'edit';
const SEGMENTS = EDIT_MODE ? RAW.slice(1) : RAW;
const PROBLEM_NUMBER = SEGMENTS[0];
const FILENAME = SEGMENTS[SEGMENTS.length - 1];
const LANGUAGE = document.body.dataset.language;
// Editing is only offered on the /edit/ route; the read-only viewer never edits.
// Editability follows the server-set language (data-language) — set for real solution
// files, the HTML stubs, and the progress file, but empty for the generated
// `solutions` view and non-source resources. HTML edits as plain text (the vendor
// bundle has no HTML LANG_EXT), but saves verbatim.
const EDITABLE = EDIT_MODE && ['python', 'c', 'json', 'html'].includes(LANGUAGE);
// Only real source files can be deleted.
const DELETABLE = /\.(py|c)$/.test(FILENAME);

// Save / Delete and the filename / language / lint status live in the editor's own
// toolbar (code.html); Eval is a global action in the workspace command bar. The
// short language label shown on the badge.
const BADGE = {python: 'PY', c: 'C', json: 'JSON', html: 'HTML'}[LANGUAGE] || (LANGUAGE || '').toUpperCase();
const outputEl = document.getElementById('save-output');
const lintEl = document.getElementById('lint-status');

// All command feedback (result line + captured output) goes to the output panel;
// kind ('ok' | 'error' | '') tints it.
function showOutput(text, kind) {
    outputEl.textContent = text;
    outputEl.className = kind ? `output-${kind}` : '';
    outputEl.hidden = !text;
}

// CodeMirror language extension for the file's language (none for generated views).
const LANG_EXT = {python: python(), c: cpp(), json: json()}[LANGUAGE] || [];

// A light editing box (default dark-on-light syntax is comfortable for editing) framed
// by dark chrome: the line-number gutter is dark, aligned with the shell's theme. As a
// theme extension (not plain CSS) it reliably overrides CodeMirror's injected base theme.
const MONO = "'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'SF Mono', 'Consolas', monospace";
const editorTheme = EditorView.theme({
    '&': {backgroundColor: '#edeff3', color: '#2a3048'},
    '&.cm-focused': {outline: 'none'},
    '.cm-scroller': {fontFamily: MONO, fontSize: '13px', lineHeight: '1.55'},
    '.cm-content': {padding: '14px 0', caretColor: '#2a3048'},
    '.cm-cursor, .cm-dropCursor': {borderLeftColor: '#2a3048'},
    '.cm-activeLine': {backgroundColor: '#e3e7f0'},
    '.cm-selectionBackground, .cm-content ::selection': {backgroundColor: '#cfe3fb'},
    '&.cm-focused .cm-selectionBackground': {backgroundColor: '#bcd8f6'},
    '.cm-gutters': {backgroundColor: '#21252b', color: '#7d8799', border: 'none', borderRight: '1px solid #3b414d'},
    '.cm-activeLineGutter': {backgroundColor: '#2a2f3a', color: '#abb2bf'},
});

// Editable source files start read-only and are switched on once the header is ready
// (generated views stay read-only) by reconfiguring this compartment.
const editable = new Compartment();
const editExt = on => [EditorView.editable.of(on), EditorState.readOnly.of(!on)];

// Only real source files are linted, and only in the editor; JSON / generated /
// read-only views have no server linter.
const LINTABLE = EDIT_MODE && /\.(py|c)$/.test(FILENAME);

// Lint the live buffer by sending it to /edit/lint, where the server runs the same
// validators as save (flake8 for Python, the runner-aware compile for C) and returns
// structured diagnostics. CodeMirror renders them as inline squiggles + gutter marks.
async function lintSource(v) {
    if (!LINTABLE) return [];
    let diagnostics = [];
    try {
        const r = await fetch('/edit/lint', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: FILENAME, content: v.state.doc.toString()}),
        });
        if (r.ok) ({diagnostics = []} = await r.json());
    } catch { /* server unreachable: no diagnostics */ }
    if (lintEl) {
        const n = diagnostics.length;
        lintEl.hidden = false;
        lintEl.textContent = n === 0 ? '● lint clean' : `● ${n} issue${n > 1 ? 's' : ''}`;
        lintEl.className = 'lint-status ' + (n === 0 ? 'ok' : 'bad');
    }
    const doc = v.state.doc;
    return diagnostics.map(d => {
        const line = doc.line(Math.min(Math.max(d.line, 1), doc.lines));
        const from = Math.min(line.from + Math.max((d.col || 1) - 1, 0), line.to);
        return {from, to: line.to, severity: d.severity || 'error', source: d.code, message: d.message};
    });
}

const editorEl = document.getElementById('editor');
const view = new EditorView({
    parent: editorEl,
    doc: document.getElementById('source').value,
    extensions: [
        // basicSetup bundles the IDE essentials: line-number gutter, history/undo,
        // bracket matching & closing, autocompletion, code folding, search panel,
        // active-line + selection-match highlighting, and the default keymaps.
        basicSetup,             // default (light) highlight style — dark-on-light tokens
        editorTheme,            // light editing box + dark gutter (overrides the base theme)
        LANG_EXT,
        indentUnit.of('    '),  // 4-space indentation (project style), not CM's 2-space default
        lintGutter(),
        linter(lintSource, {delay: 500}),
        editable.of(editExt(false)),  // read-only until enableEditing() wires it up below
        // Tab indents (matching CodeJar's catchTab); Ctrl/Cmd+S saves.
        keymap.of([
            indentWithTab,
            {key: 'Mod-s', preventDefault: true, run: () => { save(); return true; }},
        ]),
        // Clear stale command feedback as soon as the document changes.
        EditorView.updateListener.of(u => {
            if (u.docChanged && !outputEl.hidden) showOutput('', '');
        }),
    ],
});

// CodeJar parity: read the current source / flip the editable state.
const getSource = () => view.state.doc.toString();
function setEditable(canEdit) {
    view.dispatch({effects: editable.reconfigure(editExt(canEdit))});
}

// ── Editor toolbar: Save / Delete + filename / language / lint status live locally
// in this page (code.html), so the editor is self-contained — Eval is global, in the
// workspace command bar.
const saveBtn = document.getElementById('save-btn');
const delBtn = document.getElementById('del-btn');

// The filename and language badge show for every view (read-only included); Save /
// Del and editing turn on only for an editable source file.
function fillMeta() {
    const fn = document.getElementById('filename');
    if (fn) fn.textContent = FILENAME;
    const badge = document.getElementById('lang-badge');
    if (badge && BADGE) { badge.hidden = false; badge.textContent = BADGE; }
}

function enableEditing() {
    if (!EDITABLE) return;  // generated / read-only views stay read-only with no Save / Del
    saveBtn.hidden = false;
    saveBtn.disabled = false;
    saveBtn.title = 'Save (Ctrl/Cmd+S)';
    setEditable(true);
    if (LINTABLE) forceLinting(view);  // surface diagnostics without waiting for an edit
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
            body: getSource(),
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

// The toolbar buttons are in this page's own DOM (this module runs after it parses),
// so wire them directly — no shared header to wait on.
if (saveBtn) saveBtn.addEventListener('click', save);
if (delBtn) delBtn.addEventListener('click', runDelete);
fillMeta();
enableEditing();