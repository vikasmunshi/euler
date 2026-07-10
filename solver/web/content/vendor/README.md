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

Fetch (pinned):

```bash
V=2.0.4
curl -sSfL -o htmx.min.js "https://unpkg.com/htmx.org@${V}/dist/htmx.min.js"
printf 'sha384-%s\n' "$(openssl dgst -sha384 -binary htmx.min.js | openssl base64 -A)"
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
