# Vendored front-end dependencies

These third-party assets are bundled so the web front end runs fully offline, with no
CDN calls. Each is redistributed under a permissive license that allows it; the full
license text for every dependency lives in [`LICENSES/`](LICENSES/).

| File(s) | Project | Version | License | Source |
|---|---|---|---|---|
| `xterm.js`, `addon-fit.js`, `xterm.css` | xterm.js | 5.x | MIT | https://github.com/xtermjs/xterm.js |
| `highlight.min.js`, `highlight.css` | highlight.js (core + Default theme) | 10.7.0 | BSD-3-Clause | https://github.com/highlightjs/highlight.js |
| `codejar.js` | CodeJar | 4.x | MIT | https://github.com/antonmedv/codejar |
| `codemirror/*.js` (bundle entry `codemirror/cm6.js`) | CodeMirror 6 (+ @codemirror/lang-python, lang-cpp, lang-json, theme-one-dark; @lezer/*; style-mod, crelt, w3c-keyname) | 6.x | MIT | https://github.com/codemirror/dev |
| `mathjax/tex-mml-chtml.js`, `mathjax/output/chtml/fonts/woff-v2/*` | MathJax | 3.2.2 | Apache-2.0 | https://github.com/mathjax/MathJax |
| `devicon-python-original.svg`, `devicon-c-original.svg`, `devicon-json-original.svg` | Devicon | — | MIT | https://github.com/devicons/devicon |

## Notes

- **MathJax** is a subset of the npm `mathjax@3.2.2` distribution: the combined
  `tex-mml-chtml.js` component plus the CHTML `woff-v2` fonts it loads at render time.
  The font directory layout is preserved because MathJax resolves font URLs relative to
  the loaded script (`[mathjax]/output/chtml/fonts/woff-v2`). Files are copied verbatim;
  none were modified.
- **CodeMirror 6** lives under `codemirror/` as a flat set of ES modules mirrored from
  esm.sh (`target=es2022`) — the full transitive graph of `codemirror`, the language
  packages, `theme-one-dark`, `@lezer/*`, and the small helpers. Each module's absolute
  esm.sh import URLs were rewritten to relative `./<flat-name>.js` siblings, so the bundle
  loads fully offline with no CDN calls and no build step. `cm6.js` is the entry the editor
  imports (`/vendor/codemirror/cm6.js`); it re-exports only the symbols `code.js` uses. All
  `@codemirror/state` stubs re-export the single `state` build, so there is exactly one
  State instance (CodeMirror's hard requirement). To refresh, re-run the mirror against the
  desired versions; do not hand-edit the generated `*.js` files. Pin the `codemirror`
  meta-package to an explicit `6.0.x` (it is mirrored from `codemirror@6.0.2`): the bare
  `@6` range resolves to the legacy CodeMirror 5 UMD (published as `6.65.x`), which exports
  only a default `CodeMirror` object and no `EditorView` / `basicSetup`.
- The **Devicon** SVG collection is MIT-licensed. The depicted Python and C logos are
  trademarks of their respective owners — a trademark consideration, not a copyright one.
- All licenses are attribution-required: keep `LICENSES/` (and the in-file headers in
  `xterm.css` / `highlight.css`) intact when redistributing.