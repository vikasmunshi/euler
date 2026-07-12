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
  Compartment, EditorView, basicSetup, indentUnit, keymap, indentWithTab, placeholder,
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

/* The buffer's chrome is the shell's own: every surface comes from the site.css
   palette tokens, which already flip with the theme — so one theme serves both,
   and the editor is the same shade of dark (or light) as the panel around it.
   The selectors carry `&.cm-editor` rather than a bare `&`: dark stacks this on
   top of the vendored oneDark (kept for its syntax colours alone), and the extra
   class is what outranks oneDark's own background and gutters. */
function chrome(dark) {
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
  }, { dark });
}

//: Dark = oneDark's syntax palette under the shell's chrome; light = the
//: chrome over basicSetup's default (light) syntax colours.
const themeOf = (dark) => (dark ? [oneDark, chrome(true)] : [chrome(false)]);

/* The theme is a compartment, not a fixed extension: the header slider flips
   data-theme on <html> long after an editor has mounted, and a buffer left in
   the other theme is the one thing on the page that ignores the switch. Every
   live view is rethemed in place on a data-theme change (and, with no explicit
   choice stored, on the OS preference changing under us). */
const themeConf = new Compartment();
const views = new Set();
let watching = false;

function retheme() {
  const dark = isDark();
  views.forEach((view) => {
    if (!view.dom.isConnected) { views.delete(view); view.destroy(); return; }  // swapped away
    view.dispatch({ effects: themeConf.reconfigure(themeOf(dark)) });
  });
}

function watchTheme() {
  if (watching) { return; }
  watching = true;
  new MutationObserver(retheme).observe(document.documentElement,
    { attributes: true, attributeFilter: ['data-theme'] });
  matchMedia('(prefers-color-scheme: light)').addEventListener('change', retheme);
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
      themeConf.of(themeOf(dark)),                      // follows the shell's theme, live
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
  watchTheme();
  root.querySelectorAll('textarea.editor-buffer[data-cm]').forEach(enhance);
}
