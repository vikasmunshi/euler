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
| `mathjax/tex-mml-chtml.js` (+ `mathjax/output/…/woff-v2/*.woff`) | [MathJax](https://www.mathjax.org) | 3.2.2 | Apache-2.0 | `Wuix6BuhrWbjDBs24bXrjf4ZQ5aFeFWBuKkFekO2t8xFU0iNaLQfp2K6/1Nxveei` |
| `codemirror/*.js` (entry `codemirror/cm6.js`) | [CodeMirror 6](https://codemirror.net) (+ lang-python/cpp/json, theme-one-dark, @lezer/\*) | 6.0.2 | MIT | ES modules — dynamic-imported, `'self'` (no SRI) |
| `xterm/xterm.js` | [xterm.js](https://xtermjs.org) (`@xterm/xterm`) | 5.5.0 | MIT | `M169f14mRZOXm3hD/v2Ti0ThIT/RnAQagXA9nlE15yHAtrW19gdePJh/HaTzUOe/` |
| `xterm/xterm-addon-fit.js` | [`@xterm/addon-fit`](https://github.com/xtermjs/xterm.js) | 0.10.0 | MIT | `iF+jqbuti4XlB64clWgFWYEscb+UnSRv3VgVikGYZu+otNFnSHr7y7NcKfBnGizn` |
| `xterm/xterm.css` | `@xterm/xterm` (stylesheet) | 5.5.0 | MIT | `8Xk9wy/gzEDUKrXtrmCFa2bBuK3BpjpDuL/p0SeKQX19Khl/M+lHOgD/CyYf7efP` |

MathJax typesets the `$…$` TeX in statements/notes (config + re-typeset-on-swap
in `/assets/site.js`); the woff fonts are loaded by the bundle relative to its
own URL, so the whole tree ships together. Its full license text is at
`mathjax/LICENSE`. Note: MathJax injects its stylesheet at runtime — the reason
`style-src` carries `'unsafe-inline'` (docs/secure-web-server.md §4.7).

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

**xterm.js** is the terminal in the right pane (`/terminal`, Phase 6): the UMD
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
