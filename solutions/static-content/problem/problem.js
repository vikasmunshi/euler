// Renders test cases, results, and notes for a problem page.
// Mirrors the logic that used to live in solver/core/elements.py.

// MathJax v3 configuration — assigned before the deferred MathJax loader runs (this
// script is deferred ahead of it), so the loader reads it on init. typesetPromise()
// is called from loadAll() once the statement and notes are injected.
window.MathJax = {tex: {inlineMath: [["$", "$"]], displayMath: [["$$", "$$"]]}};

// Derive the problem number from the URL (e.g. "/0001/" or "/0001/problem.html").
function getProblemNumber() {
    const seg = window.location.pathname.split('/').filter(Boolean)[0];
    return parseInt(seg, 10);
}

const PROBLEM_NUMBER = getProblemNumber();

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
}

function localDate(s) {
    const d = new Date(s + ' GMT');
    if (isNaN(d.getTime())) return s;
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = String(d.getDate()).padStart(2, '0');
    const month = months[d.getMonth()];
    const year = String(d.getFullYear());
    return `${day} ${month} ${year}`;
}

// Mirror Python repr() for the value types we expect in test cases / args.
// List elements are repr()'d, matching Python (e.g. [2, 45] -> "[2, 45]").
function pyRepr(v) {
    if (Array.isArray(v)) return '[' + v.map(pyRepr).join(', ') + ']';
    if (typeof v === 'string') return "'" + v.replace(/'/g, "\\'") + "'";
    if (v === null || v === undefined) return 'None';
    if (v === true) return 'True';
    if (v === false) return 'False';
    return String(v);
}

// Mirror Python str(): same as repr() except top-level strings are unquoted.
// The harness builds the args string with str(v) on each input value.
function pyStr(v) {
    if (typeof v === 'string') return v;
    return pyRepr(v);
}

function fmtElapsed(seconds) {
    if (seconds < 1e-6) return `${Math.round(seconds * 1e9)} ns`;
    if (seconds < 1e-3) return `${(seconds * 1e6).toFixed(2)} µs`;
    if (seconds < 1) return `${(seconds * 1e3).toFixed(2)} ms`;
    return `${seconds.toFixed(3)} s`;
}

// The /solutions endpoint and results.json name C solutions "p0001_s0_c"
// (underscore), but the file served on disk is "p0001_s0.c" — map back for links.
function solutionHref(solution) {
    if (solution.endsWith('_c')) return solution.slice(0, -2) + '.c';
    return solution;
}

// Language of a solution name: C solutions end in "_c", Python in ".py".
function solutionLang(solution) {
    return solution.endsWith('_c') ? 'c' : 'py';
}

// Parse JSON while preserving integers that exceed JS's safe range as BigInt.
// Project Euler args/answers routinely exceed 2**53, and results.json stores
// args as exact strings; reading them as plain doubles would round them and
// break the test-case lookup in renderSolutions. Uses the source-text-aware
// reviver (ES2023) so we can reconstruct the exact integer from its literal.
function parseJsonBigInt(text) {
    return JSON.parse(text, (key, value, context) => {
        if (typeof value === 'number' && Number.isInteger(value) &&
            !Number.isSafeInteger(value) &&
            context && typeof context.source === 'string') {
            return BigInt(context.source);
        }
        return value;
    });
}

async function fetchJson(url, fallback) {
    try {
        // Accept: application/json tells the server this is a data fetch, so it
        // returns raw JSON rather than the human-facing JSON viewer page.
        const r = await fetch(url, {headers: {Accept: 'application/json'}});
        return r.ok ? parseJsonBigInt(await r.text()) : fallback;
    } catch {
        return fallback;
    }
}

async function fetchText(url, fallback) {
    try {
        const r = await fetch(url);
        return r.ok ? await r.text() : fallback;
    } catch {
        return fallback;
    }
}

// Per-category 1-based labels aligned with the test-case order: "dev 1", "dev 2"
// when a category has more than one case, otherwise just the category name
// ("main"). Shared by the test-case and solution tables so they read the same.
function testCaseLabels(testCases) {
    const totals = new Map();
    for (const tc of testCases) totals.set(tc.category, (totals.get(tc.category) || 0) + 1);
    const seen = new Map();
    return testCases.map(tc => {
        const idx = (seen.get(tc.category) || 0) + 1;
        seen.set(tc.category, idx);
        return totals.get(tc.category) > 1 ? `${tc.category} ${idx}` : tc.category;
    });
}

function renderTestCases(testCases) {
    const target = document.getElementById('test-cases-body');
    if (!testCases.length) {
        target.innerHTML = '<p><em>No test cases yet - someone has to go first.</em></p>';
        return;
    }
    const labels = testCaseLabels(testCases);
    const spacer = '<tr class="result-spacer"><td colspan="3"></td></tr>';
    const rows = [spacer];
    let prevCategory = null;
    testCases.forEach((tc, i) => {
        const category = tc.category;
        const inputCopy = {...tc.input};
        if ('file_url' in inputCopy && typeof inputCopy.file_url === 'string') {
            inputCopy.file_url = inputCopy.file_url.split('/').pop();
        }
        const args = Object.entries(inputCopy).map(([k, v]) => `${k}=${pyRepr(v)}`).join(', ');
        const ans = tc.answer;
        const showAnswer = ans !== null && ans !== undefined;
        const answer = showAnswer ? pyRepr(ans) : '█';
        if (prevCategory !== null && category !== prevCategory) rows.push(spacer);
        prevCategory = category;
        rows.push(
            `<tr class="result-${escapeHtml(category)}">` +
            `<td>${escapeHtml(labels[i])}</td>` +
            `<td>${escapeHtml(args)}</td>` +
            `<td>${escapeHtml(answer)}</td>` +
            `</tr>`
        );
    });
    target.innerHTML = '<table id="test-cases-table"><tbody>' + rows.join('') + '</tbody></table>';
}

// One row per solution file, one column per test case (labelled "<category> <i>"
// with i the 0-based index of the test case in test_cases.json). Each cell shows
// the result for that (solution, test case): verdict marker plus timing when
// correct, and a ⚡ on the fastest correct solution for that test case.
function renderSolutions(testCases, results, solutions, problemsJson) {
    const target = document.getElementById('solutions-body');
    const problemInfo = problemsJson[PROBLEM_NUMBER] || problemsJson[String(PROBLEM_NUMBER)] || {};
    const solvedDate = problemInfo.date || null;
    const header = `<h4>Solved: ${solvedDate ? escapeHtml(localDate(solvedDate)) : ''}</h4>`;

    if (!solutions.length) {
        target.innerHTML = header + '\n<p><em>Solution pending... the mathematician is still thinking.</em></p>';
        return;
    }
    if (!testCases.length) {
        target.innerHTML = header + '\n<p><em>No test cases yet - someone has to go first.</em></p>';
        return;
    }

    // One column per test case, keyed by the same args string the harness records
    // in results.json (str(v) of each input value, space-joined). Labels match the
    // test-case table (per-category 1-based index, or bare category name).
    const labels = testCaseLabels(testCases);
    const columns = testCases.map((tc, i) => ({
        category: tc.category,
        label: labels[i],
        args: Object.values(tc.input).map(v => pyStr(v)).join(' '),
    }));

    // Result lookup keyed by (results-solution-name | args).
    const lookup = new Map();
    for (const r of results) lookup.set(`${r.solution}|${r.args}`, r);

    // Fastest correct average per language per test case, so the quickest C and
    // Python solutions for each test case can each be highlighted.
    const fastest = new Map();
    for (const r of results) {
        if (r.verdict !== 'correct') continue;
        const key = `${solutionLang(r.solution)}|${r.args}`;
        const cur = fastest.get(key);
        if (cur === undefined || r.average < cur) fastest.set(key, r.average);
    }

    // Each test case spans two columns — verdict and timing — so the two pieces
    // line up vertically down every solution row; the fastest correct solution
    // for a test case is highlighted rather than getting its own column.
    const headCells = columns.map(c =>
        `<th class="result-${escapeHtml(c.category)} group-start" colspan="2">${escapeHtml(c.label)}</th>`).join('');
    const thead = `<thead>\n<tr><th>Solution</th>${headCells}</tr>\n</thead>`;

    // A language's fastest cell is only worth highlighting when there is more
    // than one solution of that language to compare; a lone solution is trivially
    // "fastest" and gets no body-cell shading.
    const langTotals = new Map();
    for (const s of solutions) langTotals.set(solutionLang(s), (langTotals.get(solutionLang(s)) || 0) + 1);

    const rows = solutions.map(solution => {
        const lang = solutionLang(solution);
        const cells = columns.map(c => {
            const r = lookup.get(`${solution}|${c.args}`);
            if (!r) {
                return '<td class="result-missing verdict group-start">—</td>' +
                    '<td class="result-missing timing"></td>';
            }
            if (r.verdict !== 'correct') {
                return `<td class="result-incorrect verdict group-start" title="${escapeHtml(r.verdict)}">✗</td>` +
                    '<td class="result-incorrect timing"></td>';
            }
            const fast = langTotals.get(lang) > 1 && r.average === fastest.get(`${lang}|${c.args}`)
                ? ` fastest-${lang}` : '';
            return `<td class="result-correct verdict group-start${fast}">✓</td>` +
                `<td class="result-correct timing${fast}">${escapeHtml(fmtElapsed(r.average))}</td>`;
        }).join('');
        const href = solutionHref(solution);
        return `<tr><th class="solution-name lang-${lang}"><a href="${escapeHtml(href)}">${escapeHtml(solution)}</a></th>` +
            cells + `</tr>`;
    });

    target.innerHTML =
        header + '\n' +
        '<div class="table-scroll">\n' +
        '<table id="solutions-table">\n' +
        thead +
        '\n<tbody>\n' +
        rows.join('\n') +
        '\n</tbody>\n</table>\n</div>';
}

function renderProblemStatement(title, level, statementHtml) {
    if (title) document.title = `${PROBLEM_NUMBER}: ${title}`;
    const target = document.getElementById('problem-statement-content');
    if (!target) return;
    target.innerHTML =
        `<h2>${escapeHtml(`${PROBLEM_NUMBER}: ${title} (Level ${level})`)}</h2>` +
        '<h3>Problem Statement</h3>' +
        (statementHtml && statementHtml.trim()
            ? statementHtml
            : '<p><em>Problem statement unavailable.</em></p>');
}

function renderNotes(html) {
    const target = document.getElementById('solution-notes-content');
    if (html && html.trim()) {
        target.innerHTML = html;
    } else {
        target.innerHTML = '<h3>Notes:</h3><p><em>Nothing here yet - come back when the dust has settled.</em></p>';
    }
}

async function loadAll() {
    const [statementHtml, testCases, results, solutions, notesHtml, problemsJson] = await Promise.all([
        fetchText('statement.html', ''),
        fetchJson('test_cases.json', []),
        fetchJson('results.json', []),
        fetchJson('solutions', []),
        fetchText('notes.html', ''),
        fetchJson('/problems.json', {}),
    ]);
    const title = problemsJson[PROBLEM_NUMBER].title;
    const level = problemsJson[PROBLEM_NUMBER].level;
    renderProblemStatement(title, level, statementHtml);
    renderTestCases(testCases);
    renderSolutions(testCases, results, solutions, problemsJson);
    renderNotes(notesHtml);
    // The statement and notes are injected after load, so typeset their math now.
    if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise();
}

document.addEventListener('DOMContentLoaded', loadAll);

// ── Workspace action buttons (init / reset / eval) ──
// These live in the shared header (header.js) and are gated by the workspace flags:
//   init  — enabled when authoritative and this problem is NOT already active
//   reset — enabled when authoritative and this problem IS active
//   eval  — enabled when authoritative and this problem IS active (evaluates all solutions)
function showCmdOutput(text, kind) {
    const el = document.getElementById('cmd-output');
    if (!el) return;
    el.textContent = text;
    el.className = kind ? `output-${kind}` : '';
    el.hidden = !text;
}

function applyCmdButtonState(buttons, flags) {
    const auth = !!flags.authoritative;
    const active = !!flags.active;
    buttons.init.disabled = !(auth && !active);   // nothing to init once it is the active workspace
    buttons.reset.disabled = !(auth && active);   // reset / eval need the problem in the workspace
    buttons.eval.disabled = !(auth && active);
    for (const b of Object.values(buttons)) b.hidden = false;
}

async function runWorkspaceCmd(buttons, body, label) {
    showCmdOutput(`${label}…`, '');
    for (const b of Object.values(buttons)) b.disabled = true;
    try {
        const r = await fetch(`/${PROBLEM_NUMBER}/cmd`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body),
        });
        const res = await r.json().catch(() => ({}));
        showCmdOutput(res.output || (r.ok ? `${label} ok` : `${label} failed`), r.ok ? 'ok' : 'error');
    } catch {
        showCmdOutput('network error', 'error');
    }
    // The workspace may have changed: refresh the gating flags and reload the page data.
    applyCmdButtonState(buttons, await fetchJson(`/flags?problem_number=${PROBLEM_NUMBER}`, {}));
    await loadAll();
}

function wireWorkspaceButtons(flags) {
    const buttons = {
        init: document.getElementById('init-btn'),
        reset: document.getElementById('reset-btn'),
        eval: document.getElementById('eval-btn'),
    };
    if (!buttons.init || !buttons.reset || !buttons.eval) return;
    buttons.init.title = 'Initialise this problem in the workspace';
    buttons.reset.title = 'Stack changes and clear the workspace';
    buttons.eval.title = 'Evaluate all solutions against the test cases';
    applyCmdButtonState(buttons, flags);
    buttons.init.addEventListener('click', () => runWorkspaceCmd(buttons, {cmd: 'init'}, 'init'));
    buttons.reset.addEventListener('click', () => runWorkspaceCmd(buttons, {cmd: 'reset'}, 'reset'));
    buttons.eval.addEventListener('click', () => runWorkspaceCmd(buttons, {cmd: 'eval'}, 'eval'));
}

// The buttons live in the shared header, injected asynchronously; SolverHeader.ready
// resolves with the same flags header.js fetched, so reuse them for the initial state.
window.SolverHeader.ready.then(wireWorkspaceButtons);