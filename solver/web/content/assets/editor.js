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
  EditorView, basicSetup, indentUnit, keymap, indentWithTab, placeholder,
  python, cpp, json, oneDark,
} from '/vendor/codemirror/cm6.js';

//: file language → the CodeMirror language extension (html/others: none, plain text).
const LANG = { python, c: cpp, json };

const MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';

/* The buffer's chrome is the shell's own: every surface comes from the site.css
   palette tokens, so the editor is the same shade as the panel around it.
   The selectors carry `&.cm-editor` rather than a bare `&`: this stacks on top of
   the vendored oneDark (kept for its syntax colours alone), and the extra class is
   what outranks oneDark's own background and gutters. */
function chrome() {
  return EditorView.theme({
    '&.cm-editor': {
      height: '100%',
      fontSize: '13px',
      borderRadius: '10px',
      background: 'var(--bg)',
      color: 'var(--text)',
    },
    '&.cm-editor.cm-focused': { outline: '2px solid var(--accent)', outlineOffset: '1px' },
    '&.cm-editor .cm-scroller': { fontFamily: MONO, lineHeight: '1.55' },
    '&.cm-editor .cm-content': { padding: '10px 0' },
    '&.cm-editor .cm-gutters': {
      background: 'var(--surface)',
      color: 'var(--muted)',
      border: 'none',
    },
    '&.cm-editor .cm-activeLine': { background: 'var(--surface-hi)' },
    '&.cm-editor .cm-activeLineGutter': { background: 'var(--surface-hi)', color: 'var(--text)' },
    '&.cm-editor .cm-cursor, &.cm-editor .cm-dropCursor': { borderLeftColor: 'var(--text)' },
  }, { dark: true });
}

//: oneDark's syntax palette under the shell's chrome. The site is dark-only
//: (site.css), so this is a fixed extension: there is no toggle to follow, and
//: nothing to reconfigure after a view has mounted.
const theme = [oneDark, chrome()];

/* Every live view. The Set is a strong reference, so a view stays reachable until
   `reap` drops it — which is the point: an editor whose pane has been swapped away
   must be destroyed (releasing CodeMirror's own listeners), not merely forgotten. */
const views = new Set();

//: Destroy the views whose DOM has gone. Editors mount into #content, which htmx
//: swaps wholesale, and a swap gives no notice — so the next mount is the moment
//: we know one happened, and is when we clear up after the last page.
function reap() {
  views.forEach((view) => {
    if (!view.dom.isConnected) { views.delete(view); view.destroy(); }
  });
}

function enhance(textarea) {
  if (textarea.dataset.cmMounted) { return; }
  textarea.dataset.cmMounted = '1';
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
      theme,
      langExt,
      ...(textarea.placeholder ? [placeholder(textarea.placeholder)] : []),
      indentUnit.of('    '),                            // 4-space indent (project style)
      EditorView.lineWrapping,
      keymap.of([
        indentWithTab,
        { key: 'Mod-s', preventDefault: true, run: () => { textarea.form.requestSubmit(); return true; } },
      ]),
      EditorView.updateListener.of((u) => { if (u.docChanged) { sync(view); } }),
    ],
  });
  views.add(view);
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
  reap();
  root.querySelectorAll('textarea.editor-buffer[data-cm]').forEach(enhance);
}
