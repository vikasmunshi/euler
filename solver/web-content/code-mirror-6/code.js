import {
    EditorView, basicSetup, EditorState, Compartment,
    keymap, indentWithTab, indentUnit, linter, lintGutter, forceLinting,
    python, cpp, json,
} from '/vendor/codemirror/cm6.js';

// Problem number and filename come from the URL: /<n>/<filename>.
const SEGMENTS = window.location.pathname.split('/').filter(Boolean);
const PROBLEM_NUMBER = SEGMENTS[0];
const FILENAME = SEGMENTS[SEGMENTS.length - 1];
const LANGUAGE = document.body.dataset.language;
// Only real solution files are editable; the generated `solutions` view is not.
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

// CodeMirror language extension for the file's language (none for generated views).
const LANG_EXT = {python: python(), c: cpp(), json: json()}[LANGUAGE] || [];

// Editable source files start read-only and are switched on once the header is ready
// (generated views stay read-only) by reconfiguring this compartment.
const editable = new Compartment();
const editExt = on => [EditorView.editable.of(on), EditorState.readOnly.of(!on)];

// Only real source files are linted; JSON / generated views have no server linter.
const LINTABLE = /\.(py|c)$/.test(FILENAME);

// Lint the live buffer by sending it to /<n>/lint, where the server runs the same
// validators as save (flake8 for Python, the runner-aware compile for C) and returns
// structured diagnostics. CodeMirror renders them as inline squiggles + gutter marks.
async function lintSource(v) {
    if (!LINTABLE) return [];
    let diagnostics = [];
    try {
        const r = await fetch(`/${PROBLEM_NUMBER}/lint`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: FILENAME, content: v.state.doc.toString()}),
        });
        if (r.ok) ({diagnostics = []} = await r.json());
    } catch { /* server unreachable: no diagnostics */ }
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
        basicSetup,
        LANG_EXT,
        indentUnit.of('    '),  // 4-space indentation (project style), not CM's 2-space default
        lintGutter(),
        linter(lintSource, {delay: 500}),
        editable.of(editExt(false)),  // read-only until the header wires up editing
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

// ── Save / Eval / Delete: the buttons live in the shared header, so resolve them
// once header.js has injected it, then wire their handlers and enable editing.
let saveBtn, evalBtn, delBtn;

// Show and enable the Save / Eval / Delete buttons for an editable source file and
// make the editor writable. Generated views (e.g. `solutions`) stay read-only.
function enableEditing() {
    if (!EDITABLE) return;  // generated views stay read-only with no Save / Eval button
    saveBtn.hidden = false;
    saveBtn.disabled = false;
    saveBtn.title = 'Save (Ctrl/Cmd+S)';
    setEditable(true);
    if (LINTABLE) forceLinting(view);  // surface diagnostics without waiting for an edit
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

// Evaluate just this solution (its language + index) via the /<n>/cmd endpoint.
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