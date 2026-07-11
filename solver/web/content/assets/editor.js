/* CodeMirror 6 editor for the content shell's edit page — adopted from the
 * old-web-server editor (solver/web-content/code-mirror-6/code.js) and fitted to
 * the new site as **progressive enhancement**: it upgrades the edit form's plain
 * <textarea name="content"> in place, syncing the buffer back to the textarea so
 * the existing htmx POST → 5c validation gate flow is untouched (no-JS still
 * edits the plain textarea and submits). Lazy-imported by site.js only on an edit
 * page, so its ~630 KB vendored graph never loads elsewhere.
 *
 * ES module, same-origin ('self'); CodeMirror injects its stylesheet at runtime
 * (covered by the CSP style-src 'unsafe-inline', §4.7). No eval. */
import {
  EditorView, basicSetup, indentUnit, keymap, indentWithTab,
  python, cpp, json, oneDark,
} from '/vendor/codemirror/cm6.js';

//: file language → the CodeMirror language extension (html/others: none, plain text).
const LANG = { python, c: cpp, json };

const MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';

function isDark() {
  const chosen = document.documentElement.dataset.theme;
  if (chosen) { return chosen === 'dark'; }             // the shell's explicit toggle
  return !matchMedia('(prefers-color-scheme: light)').matches;   // else OS, dark-first
}

function editorTheme(dark) {
  return EditorView.theme({
    '&': { height: '100%', fontSize: '13px', borderRadius: '10px' },
    '.cm-scroller': { fontFamily: MONO, lineHeight: '1.55' },
    '.cm-content': { padding: '10px 0' },
    '.cm-gutters': { border: 'none' },
    '&.cm-focused': { outline: '2px solid var(--accent)', outlineOffset: '1px' },
  }, { dark });
}

function enhance(textarea) {
  if (textarea.dataset.cmMounted) { return; }
  textarea.dataset.cmMounted = '1';
  const dark = isDark();
  const langExt = LANG[textarea.dataset.language] ? LANG[textarea.dataset.language]() : [];

  const host = document.createElement('div');
  host.className = 'cm-host';
  textarea.after(host);
  textarea.style.display = 'none';                      // keep it in the form as the submit source

  const sync = (view) => { textarea.value = view.state.doc.toString(); };
  const view = new EditorView({
    parent: host,
    doc: textarea.value,
    extensions: [
      basicSetup,                                       // gutter, history, brackets, search, folding…
      ...(dark ? [oneDark] : []),                       // match the shell's theme
      langExt,
      indentUnit.of('    '),                            // 4-space indent (project style)
      EditorView.lineWrapping,
      keymap.of([
        indentWithTab,
        { key: 'Mod-s', preventDefault: true, run: () => { textarea.form.requestSubmit(); return true; } },
      ]),
      EditorView.updateListener.of((u) => { if (u.docChanged) { sync(view); } }),
      editorTheme(dark),
    ],
  });
  // Belt-and-suspenders: guarantee the textarea holds the latest buffer at submit.
  textarea.form.addEventListener('submit', () => sync(view));

  // The editor often mounts during an htmx swap, before the flex container has its
  // final height — CodeMirror would then lay out against a 0-height box (gutter
  // stacked above the content). Re-measure once layout settles so the gutter sits
  // beside the code and the scroller fills the pane.
  requestAnimationFrame(() => view.requestMeasure());
  return view;
}

//: (Re)mount CodeMirror on every enhanceable textarea under *root* (the swapped
//: #content, or the document on first load). Idempotent per textarea.
export function mount(root = document) {
  root.querySelectorAll('textarea.editor-buffer[data-cm]').forEach(enhance);
}
