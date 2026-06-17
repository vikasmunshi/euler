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

// Header nav links that need the problem number (mirrors problem.js renderPageHeader):
// View on Project Euler and View on GitHub. Back-to-problem, Summary, and the inert
// "next" dummy are static in the markup.
const num = parseInt(PROBLEM_NUMBER, 10);
const p = String(num).padStart(4, '0');
document.getElementById('nav-euler').href = `https://projecteuler.net/problem=${num}`;
document.getElementById('nav-github').href =
    `https://github.com/vikasmunshi/euler/blob/master/solutions/${p[0]}/${p[1]}/${p[2]}/${p[3]}/`;

// Show the language's logo (vendored Devicon SVG); full name stays in the title.
const LANG_ICONS = {
    python: 'devicon-python-original.svg',
    c: 'devicon-c-original.svg',
    json: 'devicon-json-original.svg'
};
const langBadge = document.getElementById('lang-badge');
const iconFile = LANG_ICONS[LANGUAGE];
if (iconFile) {
    const icon = document.createElement('img');
    icon.src = `/vendor/${iconFile}`;
    icon.alt = LANGUAGE;
    langBadge.appendChild(icon);
} else {
    langBadge.textContent = LANGUAGE;  // unknown language: fall back to text
}

const saveBtn = document.getElementById('save-btn');
const evalBtn = document.getElementById('eval-btn');
const delBtn = document.getElementById('del-btn');
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
jar.updateCode(document.getElementById('source').value);

// CodeJar makes the element editable on init; gate that on /flags like before.
// 'plaintext-only' keeps paste/Enter from injecting markup into the source.
function setEditable(canEdit) {
    editorEl.setAttribute('contenteditable', canEdit ? 'plaintext-only' : 'false');
}

setEditable(false);  // read-only until /flags confirms we may save

// Clear stale command feedback as soon as the document changes.
jar.onUpdate(() => {
    if (!outputEl.hidden) showOutput('', '');
});

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
        const r = await fetch(`/${PROBLEM_NUMBER}/flags`, {headers: {Accept: 'application/json'}});
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
    if (saveBtn.disabled) return;
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
        const r = await fetch(`/${PROBLEM_NUMBER}/eval`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
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

saveBtn.addEventListener('click', save);
evalBtn.addEventListener('click', runEval);
delBtn.addEventListener('click', runDelete);
refreshFlags();