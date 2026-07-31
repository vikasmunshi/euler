# Vendored front-end assets

The web front end serves all third-party JavaScript locally so it runs fully
offline (no CDN calls) and under a strict `script-src 'self'` CSP. Each file is
pinned by version and integrity hash and served from `/vendor` by Caddy.

To refresh a pin, re-run the fetch below, update the version + SRI here, and
update the `<script integrity="…">` in the templates that load it.

## Inventory

| File | Package | Version | License | SRI (sha384) |
|------|---------|---------|---------|--------------|
| `htmx.min.js` | [htmx](https://htmx.org) | 2.0.4 | 0BSD | `HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+` |
| `mathjax/tex-mml-chtml.js` (+ `mathjax/output/…/woff-v2/*.woff`, `mathjax/input/tex/extensions/*.js`) | [MathJax](https://www.mathjax.org) | 3.2.2 | Apache-2.0 | `Wuix6BuhrWbjDBs24bXrjf4ZQ5aFeFWBuKkFekO2t8xFU0iNaLQfp2K6/1Nxveei` (bundle; the autoloaded extensions are `'self'`, no SRI) |
| `codemirror/*.js` (entry `codemirror/cm6.js`) | [CodeMirror 6](https://codemirror.net) (+ lang-python/cpp/json, theme-one-dark, @lezer/\*) | 6.0.2 | MIT | ES modules — dynamic-imported, `'self'` (no SRI) |
| `xterm/xterm.js` | [xterm.js](https://xtermjs.org) (`@xterm/xterm`) | 5.5.0 | MIT | `M169f14mRZOXm3hD/v2Ti0ThIT/RnAQagXA9nlE15yHAtrW19gdePJh/HaTzUOe/` |
| `xterm/xterm-addon-fit.js` | [`@xterm/addon-fit`](https://github.com/xtermjs/xterm.js) | 0.10.0 | MIT | `iF+jqbuti4XlB64clWgFWYEscb+UnSRv3VgVikGYZu+otNFnSHr7y7NcKfBnGizn` |
| `xterm/xterm.css` | `@xterm/xterm` (stylesheet) | 5.5.0 | MIT | `8Xk9wy/gzEDUKrXtrmCFa2bBuK3BpjpDuL/p0SeKQX19Khl/M+lHOgD/CyYf7efP` |

MathJax typesets the `$…$` TeX in statements/notes (config + re-typeset-on-swap
in `/assets/site.js`); the woff fonts are loaded by the bundle relative to its
own URL, so the whole tree ships together. Its full license text is at
`mathjax/LICENSE`. Note: MathJax injects its stylesheet at runtime — the reason
`style-src` carries `'unsafe-inline'` (docs/web-server-guide.md § Content-Security-Policy).

**The TeX extensions under `mathjax/input/tex/extensions/`** ship for the same
reason as the fonts: the combined bundle carries only the default packages, and the rest
are fetched relative to the bundle's own URL, so
`/vendor/mathjax/input/tex/extensions/<name>.js`. Vendored, that request is
same-origin and `script-src 'self'` admits it; *not* vendored it 404s, and the
`noundefined` package then renders the macro as its own name in red — which is what a
statement using `\color` used to show (problem 230).

**They are preloaded, not autoloaded** (`loader.load` + `tex.packages` in
`/assets/site.js`). MathJax's `autoload` fetches a package **on first use**, i.e. in the
middle of a typeset, and the swap path lost that race: a statement reached by the
terminal's `show` rendered `\color[RGB]124, 192, 255` as literal text while a plain
refresh of the same URL was perfect. Preloading costs one fetch per document, of files
already vendored, and makes the typesetter's vocabulary independent of which page the
reader happened to open first. **A package added here must be added to `MJ_TEX` in
site.js as well** — preloading a name whose file is missing fails MathJax *startup*, on
every page, which is worse than the autoload it replaced. A test pins both directions
(`tests/test_web_verbs.py::MathJaxWiringTests`).

One file per package actually used by a cached statement, found by scanning them for
each trigger macro:

| Package | Macros | Statements |
|---------|--------|------------|
| `color` | `\color`, `\textcolor`, … | 12, e.g. 40 · 66 · 230 |
| `mhchem` | `\pu`, `\ce` | 5, e.g. 75 · 155 · 222 |
| `html` | `\style`, `\class`, `\href` | 3: 282 · 326 · 334 |
| `boldsymbol` | `\boldsymbol` | 2: 323 · 462 |
| `enclose` | `\enclose` | 1: 535 |
| `unicode` | `\unicode` | 1: 991 |

A statement that starts using another one is the same fix: add the file, re-run the
scan. There is no SRI — these are same-origin scripts MathJax injects itself, exactly
like the CodeMirror modules.

**CodeMirror 6** is the code editor on the edit page (`/assets/editor.js`,
lazy-imported by `site.js` only when an editor appears, so the ~630 KB graph
never loads elsewhere). It lives under `codemirror/` as a flat set of ES modules
mirrored from esm.sh (`target=es2022`) with imports rewritten to relative `./`
siblings — the full transitive graph of `codemirror`, the language packages,
`theme-one-dark`, `@lezer/*`, and helpers — so it loads fully offline with no
build step. `cm6.js` is the entry (re-exports only the symbols `editor.js` uses).
Pin the `codemirror` meta-package to an explicit `6.0.x`: the bare `@6` range
resolves to the legacy CodeMirror 5 UMD, which has no `EditorView`/`basicSetup`.
All `@codemirror/state` stubs re-export one `state` build (CM's single-instance
rule). Like MathJax it injects its stylesheet at runtime (`style-src
'unsafe-inline'`). Dynamic-imported same-origin modules, so no SRI. License at
`codemirror/LICENSE`.

**xterm.js** is the terminal in the right pane (`/terminal`): the UMD
`xterm.js` plus the **fit** addon (it sizes the terminal to its container; the
resulting `cols`×`rows` is what `terminal.js` sends over the socket as the PTY's
geometry) and the stock stylesheet. Classic scripts with SRI — unlike CodeMirror
they are not ES modules, so they are `<script src>`-loaded by `terminal.html` and
integrity-checked. Both files carry a `//# sourceMappingURL=` line whose `.map` is
**not** vendored: harmless (only devtools ever requests it), and stripping it
would make the bytes diverge from the published ones the SRI above attests.
License at `xterm/LICENSE`.

Fetch (pinned):

```bash
V=2.0.4
curl -sSfL -o htmx.min.js "https://unpkg.com/htmx.org@${V}/dist/htmx.min.js"
printf 'sha384-%s\n' "$(openssl dgst -sha384 -binary htmx.min.js | openssl base64 -A)"

V=3.2.2   # MathJax: the single-file combined component + its woff-v2 fonts
curl -sSfL -o mathjax/tex-mml-chtml.js "https://cdn.jsdelivr.net/npm/mathjax@${V}/es5/tex-mml-chtml.js"
# fonts: es5/output/chtml/fonts/woff-v2/*.woff from the same release
# the autoloaded TeX extensions the cached statements use (see the table above)
mkdir -p mathjax/input/tex/extensions
for e in color mhchem html boldsymbol enclose unicode; do
  curl -sSfL -o "mathjax/input/tex/extensions/$e.js" \
    "https://cdn.jsdelivr.net/npm/mathjax@${V}/es5/input/tex/extensions/$e.js"
done

XV=5.5.0; FV=0.10.0    # xterm.js + the fit addon (the Phase-6 terminal)
curl -sSfL -o xterm/xterm.js            "https://unpkg.com/@xterm/xterm@${XV}/lib/xterm.js"
curl -sSfL -o xterm/xterm.css           "https://unpkg.com/@xterm/xterm@${XV}/css/xterm.css"
curl -sSfL -o xterm/xterm-addon-fit.js  "https://unpkg.com/@xterm/addon-fit@${FV}/lib/addon-fit.js"
for f in xterm/xterm.js xterm/xterm.css xterm/xterm-addon-fit.js; do
  printf '%-28s sha384-%s\n' "$f" "$(openssl dgst -sha384 -binary "$f" | openssl base64 -A)"
done
```

## Licenses

### htmx — Zero-Clause BSD (0BSD)

```
Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```
