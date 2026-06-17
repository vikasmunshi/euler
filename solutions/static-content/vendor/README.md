# Vendored front-end dependencies

These third-party assets are bundled so the web front end runs fully offline, with no
CDN calls. Each is redistributed under a permissive license that allows it; the full
license text for every dependency lives in [`LICENSES/`](LICENSES/).

| File(s) | Project | Version | License | Source |
|---|---|---|---|---|
| `xterm.js`, `addon-fit.js`, `xterm.css` | xterm.js | 5.x | MIT | https://github.com/xtermjs/xterm.js |
| `highlight.min.js`, `highlight.css` | highlight.js (core + Default theme) | 10.7.0 | BSD-3-Clause | https://github.com/highlightjs/highlight.js |
| `codejar.js` | CodeJar | 4.x | MIT | https://github.com/antonmedv/codejar |
| `mathjax/tex-mml-chtml.js`, `mathjax/output/chtml/fonts/woff-v2/*` | MathJax | 3.2.2 | Apache-2.0 | https://github.com/mathjax/MathJax |
| `devicon-python-original.svg`, `devicon-c-original.svg`, `devicon-json-original.svg` | Devicon | — | MIT | https://github.com/devicons/devicon |

## Notes

- **MathJax** is a subset of the npm `mathjax@3.2.2` distribution: the combined
  `tex-mml-chtml.js` component plus the CHTML `woff-v2` fonts it loads at render time.
  The font directory layout is preserved because MathJax resolves font URLs relative to
  the loaded script (`[mathjax]/output/chtml/fonts/woff-v2`). Files are copied verbatim;
  none were modified.
- The **Devicon** SVG collection is MIT-licensed. The depicted Python and C logos are
  trademarks of their respective owners — a trademark consideration, not a copyright one.
- All licenses are attribution-required: keep `LICENSES/` (and the in-file headers in
  `xterm.css` / `highlight.css`) intact when redistributing.