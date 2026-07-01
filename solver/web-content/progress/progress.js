// Progress editor: edits the raw .progress.html file. The nav bar and the Save
// button come from the shared header (header.js); this wires Save to POST /progress
// and reports the result in the output panel, matching the code page's behaviour.

const outputEl = document.getElementById('save-output');
const contentEl = document.getElementById('content');

// All save feedback goes to the output panel; kind ('ok' | 'error' | '') tints it.
function showOutput(text, kind) {
    outputEl.textContent = text;
    outputEl.className = kind ? `output-${kind}` : '';
    outputEl.hidden = !text;
}

let saveBtn;  // resolved from the shared header once it is injected

async function save() {
    if (!saveBtn || saveBtn.disabled) return;
    saveBtn.disabled = true;
    showOutput('saving…', '');
    try {
        const resp = await fetch('/progress', {
            method: 'POST',
            headers: {'Content-Type': 'text/plain; charset=utf-8'},
            body: contentEl.value,
        });
        const text = await resp.text();
        showOutput(text || (resp.ok ? 'saved' : 'save failed'), resp.ok ? 'ok' : 'error');
    } catch {
        showOutput('network error', 'error');
    } finally {
        saveBtn.disabled = false;
    }
}

// Clear stale feedback as soon as the document changes.
contentEl.addEventListener('input', () => {
    if (!outputEl.hidden) showOutput('', '');
});

// Ctrl/Cmd+S saves (matches the code editor).
contentEl.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        save();
    }
});

// The Save button lives in the shared header, injected asynchronously; wire it once ready.
window.SolverHeader.ready.then(() => {
    saveBtn = document.getElementById('save-btn');
    saveBtn.hidden = false;
    saveBtn.disabled = false;
    saveBtn.title = 'Save the progress file (Ctrl/Cmd+S)';
    saveBtn.addEventListener('click', save);
});