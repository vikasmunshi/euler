# Content-service site design

The layout, visual identity, and URL surface of the content service
(`solver/web/site`) — the contract the view/edit sub-steps (Phase 5b–5e) build to.
The site is **one server-rendered app shell**: a persistent frame whose content pane is
swapped by **htmx** fragments, never a client-side SPA. Every route is gated by an
`object:permission` capability checked against the request's `X-Profile`
([DD-12](secure-web-server.md#dd-12--unified-authorization-solverauth--authorizationsjson))
and every response carries the per-response CSP nonce
([§4.7](secure-web-server.md), [DD-10](secure-web-server.md#dd-10--phase-5-content-service-choices)).

> **Status.** 5a–5d live; **5e (this revision — the refined shell, chrome, and page
> specs below) implemented**. Next: Phase 6 (the `/ws` terminal in the right pane).

## 1 · The app shell — four regions, one viewport

`GET /` serves the whole shell; every other path renders **into a region of it**.
The four regions are **fixed** and together occupy **exactly the viewport** — the
page itself never scrolls; each middle pane scrolls its own overflow.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HEADER  eiπ+1=0 │ Solutions · Docs · Topics │ Actions │ ⌂ crumbs… │ ◐ │ 🯅 │  fixed
├──────────────────────────────────────┬───────────────────────────────────────┤
│  LEFT PANE  (#content)                │  RIGHT PANE  (#ws)                    │
│  navigable content, htmx-swapped;     │  the solver PTY terminal over /ws     │  equal
│  deep-linkable; scrolls ↕ and ↔       │  (Phase 6); persists across left      │  width
│  when content overflows               │  swaps; scrolls ↕ when needed         │  &
│                                       │                                       │  height
├──────────────────────────────────────┴───────────────────────────────────────┤
│ FOOTER   © · license · terms of use · readme · acknowledgements               │  fixed
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Header** (fixed) — one control surface, grouped by **separators**, identical on
  every page: the brand (→ `/`) · primary nav `Solutions · Docs · Topics` · the
  **Actions** menu (page-specific verbs, §6 — labelled just "Actions", no
  caret, **always present** even when the page has none) · the **back arrow**
  (the previous page *in the pane*: the browser's back navigates the document
  and would take the terminal with it, so the pane keeps a history of its own —
  `site.js`, a swap not a navigation; on the first page of a visit it points at
  that page itself) · **breadcrumbs** (the
  current path; the leading crumb is the **euler glyph**, ancestors clickable) ·
  the **theme slider** (◐, light⇄dark) · the **user glyph** (a person icon in a
  circle) opening a sub-menu: *Account* (`/account`, left pane),
  *Change password* (`/password`, auth tier — current password + new twice, SRP,
  distinct from the unauthenticated `/forgot` reset; it renders **into the left
  pane** as a bare fragment on `HX-Request`, §9), *Logout* (`POST /auth/logout`).
- **Left pane** `#content` — the navigable region. Nav and in-page links `hx-get` a
  route and swap it here; the URL updates (`hx-push-url`) so every view is
  deep-linkable. Scrolls **both axes** when content overflows.
- **Right pane** `#ws` — a same-origin **iframe** onto `/terminal`, its own
  document (the pattern proven by the parked front end, where the terminal and
  the content lived in separate browsing contexts). The terminal talks only to
  `/ws`; **left-pane navigation is htmx-only and can never touch the iframe's
  document**, so the session persists structurally, not by discipline. Scrolls
  **vertically** inside the iframe when needed (wired in Phase 6).
- **Footer** (fixed) — © Vikas Munshi · license (`/about/license`) ·
  terms of use (`/terms`) · acknowledgements (`/about/acknowledgements`).
  Footer documents swap **into the left pane** like any other navigation
  (`hx-get` → `#content`), never touching the shell or the terminal.
  license/acknowledgements are content routes; terms is the auth tier, which
  returns a bare fragment on `HX-Request` (§9). (`/about/readme` stays routable
  but is not linked.)

**Layout principle.** `body` is a viewport-high grid (`auto 1fr auto`); the two
middle panes are **equal width and height** (`1fr 1fr`), each an independent
scroll container (`min-height: 0`). Controls never move between pages; only pane
*content* changes.

## 2 · Visual identity & theme

- **Brand — Euler's identity, `e^iπ + 1 = 0`.**
  - The **glyph/favicon** is its geometric reading on the unit circle: the
    **upper semicircle** from `1` to `−1` (the rotation by `π`) plus the **unit
    segment** from `−1` back to `0` — drawn as a two-stroke SVG in the accent
    orange. (Replaces the earlier `ς`.)
  - The **wordmark** (the home link) is the **algebraic formula**
    `e^iπ + 1 = 0` (superscript *iπ*), not the word "euler".
- **Theme — dark-first, with a remembered slider.** The dark palette is the
  primary design; light is offered via `prefers-color-scheme` and the header's
  **slider** (a two-state switch, not a button). An explicit choice is stamped as
  `data-theme` on `<html>` and **remembered** (`localStorage`, per browser) before
  first paint. Accent is a warm orange, carried through the glyph, links, and
  focus rings.

  | token | dark (primary) | light |
  |---|---|---|
  | `--bg` | `#0f1115` | `#f7f7f8` |
  | `--surface` | `#171a21` | `#ffffff` |
  | `--border` | `#2a2f3a` | `#e5e7eb` |
  | `--text` | `#e5e7eb` | `#1f2937` |
  | `--muted` | `#9ca3af` | `#6b7280` |
  | `--accent` | `#f97316` | `#f97316` |

  Theme-sensitive detail colours (grid-cell heat, file git-status) are defined as
  tokens too, with **distinct values per theme** — a light background needs
  stronger mixes than a dark one.
- Self-contained + same-origin only (CSP `'self'`): no external fonts/CDNs; system
  font stack; vendored htmx + **MathJax** from `/vendor`. Statements and notes carry
  math as TeX text (`$…$` / `$$…$$`); MathJax typesets on load and after every htmx
  swap (`site.js`). Its runtime stylesheet is why `style-src` carries
  `'unsafe-inline'` ([§4.7](secure-web-server.md)) — scripts remain nonce-only.

## 3 · Writing style — created pages

The voice of every page the service *authors* (index/landing copy, blurbs,
status lines — not the rendered guides/notes themselves):

- **Never state the obvious.** No "click a link to navigate"; no restating what
  the reader is looking at.
- **Humour, lightly.** The parked front end (branch `old-web-server`) is the
  register: "*Twelve guides stand between you and the next unsolved problem.
  Read one, ignore the rest, feel briefly invincible.*"
- **Intuitive and useful.** Every sentence either orients or enables; cut the rest.
- **Block boxes for items.** Enumerable things (guides, topics, entry points)
  render as **cards** — two/three per row — not bullet lists (§7).

## 4 · Path ownership

One host, one authenticated origin; Caddy splits paths across tiers
([frontend.sh](../scripts/setup/frontend.sh)). The content service owns only the
authenticated catch-all and must not collide with a reserved path.

| Owner | Paths | Notes |
|---|---|---|
| **Caddy-native / static** | `/healthz`, `/assets/*`, `/vendor/*`, `/favicon.ico` | served from `/etc/euler/web-content`; same-origin |
| **Auth service** (`auth.sock`) | `/login`, `/register*`, `/reset*`, `/forgot`, `/password`, `/terms`, `/auth/*` | public surface + `forward_auth` gate; **styled per §2** (shared tokens/brand, `data-theme` honoured) |
| **ws service** (`ws-<profile>.sock`, Phase 6) | `/ws` | PTY WebSocket; the right pane connects here |
| **Content service** (`content-<profile>.sock`) | everything else below | per-profile instance, chosen on `X-Profile` |

## 5 · Capability → profile floor

The web ladder caps at `maintainer` (`admin` is local-only,
[DD-11](secure-web-server.md#dd-11--profiles--content-service-access)).

| Capability | Floor | Backs |
|---|---|---|
| `web-content:read` | reader | the app shell (header/footer/panes) |
| `docs:read` | reader | guides, composed reference pages, topics |
| `solutions:read` | reader | the solutions grid, problem pages, files |
| `solutions:execute` | contributor | `eval` / `benchmark` (via `/ws`); the progress upload |
| `solutions:write` | contributor | editor, save, lint |
| `solutions:delete` | maintainer | delete a solution file |
| `ai:execute` | maintainer | regenerate notes |
| `users:read` | reader | the account page |
| `about:read` | reader | the footer pages: readme, license, acknowledgements |

The `about` **object** maps to the specific files behind the footer —
`README.md`, `LICENSE`, `solver/web/content/vendor/README.md` — so the
per-profile uids get read on exactly those (the `content.sh` ACL derivation
includes `about` in its READ set).

No-subject (bypassed Caddy) → **401**; authenticated but lacking the grant →
**403**; a per-profile instance also refuses a mismatched `X-Profile` (401 — the
`EULER_PROFILE` pin).

## 6 · Page chrome: breadcrumbs & Actions

Two header regions are **page-specific** yet live in the fixed header, which htmx
never re-renders — so every `#content` fragment response carries them as
**out-of-band swaps** (`hx-swap-oob`) alongside the pane content; a full-page
render places the same partials in the header directly. One source of truth per
page: the handler supplies `crumbs` (ancestors clickable, leaf plain) and
`actions`.

**Actions** is a dropdown of the current page's verbs, populated per route and
**filtered by the subject's grants** (hidden = UX; `requires()` on the backing
route remains the boundary). It is **always shown** (labelled "Actions", no
caret); a page with no verbs reads muted and opens to "No actions here":

| Page | Actions (floor) |
|---|---|
| `/solutions/` | Upload progress (`solutions:execute`) |
| `/solutions/{n}/` | — (none) |
| `/solutions/{n}/{file}` (editable) | Edit (`solutions:write`) · Delete (`solutions:delete`, bare `.py`/`.c`) |
| `/edit/solutions/{n}/{file}` | Save (`solutions:write`) · Delete (`solutions:delete`) |
| `/edit/solutions/` | Save (`solutions:execute`) |
| elsewhere | — (menu shown, empty) |

*Save* submits the page's editor form; *Delete* confirms, then swaps the problem
page back into `#content`. Menus (`Actions`, the user glyph) are native
`<details>` dropdowns — no JS framework, a few lines in `site.js` close them on
selection.

## 7 · Content pages

- **Landing (`/`), docs index, topics index** — visually alike: a short hero
  (kicker · title · one wry lede) over a **card grid** — each card an icon, a
  title, and a blurb that earns its place (§3). The landing stacks its entry
  points **one box per row** (Solutions · Docs · Topics · Terminal — no Account
  card; it lives in the user menu); the docs and topics indexes list their pages
  **two/three per row**. **Index cards** show the
  **filename** (separators → spaces, title-cased) as the first line and the
  page's markdown `#` title as the second, **sorted by filename**.
- **Solutions (`/solutions/`)** — the 10×10 century grids: **square cells** (and
  so square grids, via `aspect-ratio`), packed **as many per row as fit** — ~3 in
  a normal left pane, fewer/narrower or more/wider (CSS `auto-fill`, the
  old-web-server flex-wrap in grid form). Cells shaded by difficulty with
  **per-theme heat tokens** (§2), title + pct on hover. Page action: **Upload
  progress** → `/edit/solutions/`.
- **Progress upload (`/edit/solutions/`)** — an **empty** paste buffer (this is a
  *replace*, not an edit — the previous `.progress.html` is superseded wholesale);
  parse-or-reject before anything lands, success answers with the refreshed grids.
  Same furniture as the file editor (below): the buffer fills the pane, Save is an
  Actions item, no in-form button.
- **Problem (`/solutions/{n}/`)** — statement first, then **test cases · results ·
  files · notes** (in that order):
  - Two **off-site links** on the meta line: the problem on **projecteuler.net**
    and the solution directory on **github** (the repo URL is configuration —
    `EULER_GITHUB_URL` — since the service uid cannot read `.git`).
  - **Test cases** render as a table (category · input · answer), not raw JSON.
  - **Files** flow **horizontally** (wrapping as needed), plain text links — no
    underline/highlight; **zero-size files are hidden**; each name is coloured by
    its **git status** (clean/modified/staged/untracked) with the status spelled
    out in the hover title. Git status is **best-effort**: the deployed service
    uids cannot read `.git` (kept off the content ACLs by design, DD-12), so
    production shows plain names; a dev run as the owner shows the colours.
  - **Notes** rendered last (stored sanitised, 5c).

## 8 · Routes

`Fragment` = what an `hx-get`/`hx-post` from the shell renders into `#content` (or `#ws`);
a **direct** hit on the same path returns the whole shell with that pane pre-populated
(deep-link). Writes always return a fragment. Fragments carry the §6 chrome out-of-band.

### 8a — shell ✅

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/` | the app shell; left pane = the **landing** (default content), right pane = the `/terminal` iframe | `web-content:read` |
| GET | `/terminal` | the right pane's standalone document: xterm.js + the `/ws` client (Phase 6) | `web-content:read` |

### 8b — read (left-pane content) ✅

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/solutions/` | `problems.json` as **10×10 century grids** (square, auto-fit ~3/row, per-theme heat) + summary | `solutions:read` |
| GET | `/solutions/{n}/` | the `solution_dir`: statement, then test-cases · results · files · notes (§7) | `solutions:read` |
| GET | `/solutions/{n}/{filename}` | one problem file (solution source, `statement.html`, `resources/*`) | `solutions:read` |
| GET | `/docs/` | docs index (card grid) | `docs:read` |
| GET | `/docs/file/{path}` | a doc-referenced repo file (under the `docs`/`about`/`solutions` object trees only, DD-12) rendered in the viewer | `docs:read` |
| GET | `/docs/{name}` | a rendered doc — **all** guides incl. `ai` / `convention_*` (the file may live in `docs/` or elsewhere) | `docs:read` |
| GET | `/topics/` | topics index (card grid, blog-style writeups) | `docs:read` |
| GET | `/topics/{name}` | a topic page (e.g. `prime-numbers`) | `docs:read` |
| GET | `/account` | the signed-in user + profile (from `X-User` / `X-Profile`) + display name (Phase 7: edited via an auth-tier fragment, the change-password pattern — DD-15 web-git authorship) | `users:read` |
| GET | `/about/{name}` | the footer pages: `readme` · `license` · `acknowledgements` | `about:read` |

### 8c — validation (the save gate) ✅

Not routes — the checks every write passes, in `solver/web/site/validate.py`
(config-free, DD-12): `.py` (auto-fix + flake8 over stdin), `.c` (scratch-dir compile
against the runner header), `.json` re-indent, and the **`.html` gate via nh3**
(sanitize-and-store-clean — `notes.html` is served back and rendered, so raw HTML is
stored-XSS; [DD-10](secure-web-server.md#dd-10--phase-5-content-service-choices)).
`nh3` is in the `web` extra; `content.sh`'s deploy/status probes verify its import.

### 8d — edit (each write → 8c; each response carries CSP) ✅

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/edit/solutions/` | the **progress upload** (collection-level; empty buffer, §7) | `solutions:execute` |
| POST | `/edit/solutions/` | save progress → grid block + status (writes `solutions/.progress.html`) | `solutions:execute` |
| GET | `/edit/solutions/{n}/{filename}` | code-editor for the file (bare editable names; the editor edits, `new` creates) | `solutions:write` |
| POST | `/edit/solutions/{n}/{filename}` | save → editor block + status (the buffer echoes the 8c **canonical** content) | `solutions:write` |
| DELETE | `/edit/solutions/{n}/{filename}` | delete (bare `.py`/`.c` only) → the **problem page** fragment | `solutions:delete` |

**Writes always return a fragment** (never the shell). *(A notes-regenerate
route was removed: the content tier cannot reach the Claude API — no key on the
service uid, no egress, no `ai` extra — so the affordance was dropped rather than
ship a dead stub; regenerate notes via `claude-api docs {n}` in the shell. The
`ai:execute` grant thus has no web surface today. The Phase-7 `euler-ai` broker
([DD-15](secure-web-server.md#dd-15--secrets-are-brokered-never-dispensed)) is the
designed path to restore it: the maintainer content instance calls the broker —
still no key, no direct egress on the service uid.)*

### execute — via the terminal (`/ws`), Phase 6

Execution is **not** per-route POSTs; the right-pane terminal talks to `/ws`, and the
left-pane navigation never does. **Resolved
([DD-13](secure-web-server.md#dd-13--web-shell-topology--gating), since superseded by
the per-user model — [real-multi-tenant-web-access.md](real-multi-tenant-web-access.md)):
the terminal is the full `solver` shell**, not a curated command list — the stub set
once sketched here (`set`/`show`/`ls`/`eval`/`benchmark`) arrives as the real commands,
and what a web shell can run is the DD-12 decorator (`requires`) against the
ticket-resolved subject. The shell runs on **the user's own `euler-user@<slug>`
instance** (one per collaborator, serving their content *and* `/ws`), attach gated on
`solver:execute` (a `reader`-floor grant — everyone gets a terminal). Inside it the
rungs diverge: a `reader` shell registers only the read commands (`set`/`show`/`ls`,
plus `git-status`/`git-sync` — `git:read`; no `eval`/`benchmark`, no `edit`);
`contributor` adds edit + eval/benchmark and the **native** git write verbs
(`git:execute`): `git-commit`/`git-push` on **their own** `user/<slug>` branch in
their own clone, with `git-identity` the one-time gh sign-in — master lands only via
the admin's `git-merge`; `maintainer` adds delete + the AI commands (credentials =
the user's **own** Anthropic key from their vault, uploaded on the account page).
`!` (`shell:execute`) tracks its grant (ships `maintainer`+), and `admin` over web
is contained by its own uid + SRP (MT-10a/AR-4).

## 9 · Render & navigation contract

- **Shell vs fragment.** `/` returns the full shell. A read/edit path returns its
  `#content` fragment on `HX-Request` (plus the §6 chrome out-of-band), or the full
  shell with `#content` pre-populated on a direct visit — so links are shareable and
  reload-safe.
- **Navigation refreshes only the left pane.** Every in-app link swaps `#content`
  (htmx, incl. back/forward via its history handling); the shell (header, footer,
  the `#ws` iframe) is never re-rendered by navigation. Account, the footer
  documents, terms, and change password **all swap into the left pane** — the
  auth-tier pages (terms, password) return a bare fragment on `HX-Request` so
  they render in `#content` without nesting a page, and the change-password
  fragment carries its SRP scripts (htmx executes them; `srp.js` is idempotent,
  and on success `password.js` swaps the pane to `/account`). Only logout
  deliberately leaves the shell.
- **The terminal survives the shell (Phase 6 contract).** A *full* load (F5,
  address-bar entry, tab close) is the only thing that can reach the terminal —
  and the terminal iframe guards it exactly like the parked front end: a
  `beforeunload` confirmation armed while its WebSocket is open, disarmed on
  disconnect/close and on deliberate exits (the shell posts
  `{euler: 'disarm'}` to the iframe before logout). The PTY itself survives
  server-side regardless (one persistent shell per user, replay on reconnect) —
  the dialog protects the *scrollback and flow*, not the process.
- **Canonical trailing slash.** Every GET path is canonical *with* its trailing slash
  (`/solutions/`, `/docs/`, `/topics/`, `/solutions/{n}/`, `/edit/solutions/`). A GET
  missing the slash → **301** redirect to the slashed form, so each view has one URL.
- **Terminal persistence.** htmx swaps only `#content`; `#ws` (the terminal) is untouched
  by navigation and keeps its session.
- **Rendered-doc links.** `render_markdown` rewires a doc's links for the shell: a
  `foo.md` cross-link → the `/docs/` (or `/topics/`) route; a repo-relative
  `../<path>` → the `/docs/file/<path>` viewer (so one authored link resolves both on
  GitHub and in-app); and every internal `/…` link is given `hx-*` so it swaps the
  pane in place. External and `#anchor` links are left alone here — they are handled
  by the rule below.
- **Every off-site link opens in a new tab.** `site.js` stamps `target="_blank"
  rel="noopener noreferrer"` on any link whose host is not ours, on load and after
  every swap. It is a document-wide rule, not per-link markup, precisely because the
  riskiest links are the ones we do not author: the cached projecteuler.net
  statements and the notes' reference links. Following one in place would tear down
  the shell — and with it the terminal, which §9 promises never to lose.
- **Nav (fixed header):** brand → `/`, `Solutions` → `/solutions/`, `Docs` → `/docs/`,
  `Topics` → `/topics/`, user glyph → account / password / logout (all left pane
  but logout). Profile-gated
  affordances (the Actions menu, §6) are hidden from profiles that lack them; the
  route still enforces the gate server-side — hiding is UX, `requires()` is the
  boundary.

## 10 · Decisions & consequences

1. **App-shell layout** — one page `/`, four regions (§1); content is htmx fragments into
   `#content`, terminal in `#ws`. ✅
2. **URL scheme under `/solutions/`** (`/solutions/{n}/`, `/edit/solutions/{n}/{filename}`).
   `core/viewer.py` emits `show` → `/solutions/NNNN/`, `edit` →
   `/edit/solutions/NNNN/<file>`. ✅
3. **Folded away:** `/summary` → the `/solutions/` century grids; `/ai/{name}` →
   `/docs/{name}`; `/{n}/cmd` → the `/ws` command set. The **progress upload** is the
   collection-level `/edit/solutions/` (GET/POST, no DELETE), gated `solutions:execute`
   — contributor-floored, so the existing `euler-sol-write` ACL already covers its write to
   `solutions/.progress.html`: no `progress:write` grant and no new ACL. ✅
4. **`topics/` is a new content tree** (blog-style), in the `docs` object → the
   `euler-sol-read` ACL, gated `docs:read`. ✅
   A problem's `topics` field is **new data** — needs a per-problem tagging source. ⬜
5. **Data:** `level` / `pct` / `solved` / `date` come from `problems.json` today; `topics`
   does not (see 4). Difficulty renders from `Problem.difficulty`.
6. **Execute via `/ws`** — resolved as the **full solver shell** gated by the DD-12
   decorator (not a curated command set); per-profile instances for all three web
   rungs, attach = `solver:execute` (reader-floor, so every account gets a
   terminal — a `reader`'s is read-only, no shell escape); `!` stays admin-only
   (never web), AI at `maintainer` via the Phase-7 `euler-ai` broker
   ([DD-13](secure-web-server.md#dd-13--web-shell-topology--gating) /
   [DD-15](secure-web-server.md#dd-15--secrets-are-brokered-never-dispensed)). ✅
7. **Full-viewport shell (5e).** The four regions fill the viewport exactly; the panes
   are equal (`1fr 1fr`) independent scroll containers (left ↕↔, right ↕). ✅
8. **Brand = Euler's identity (5e).** Geometric glyph (semicircle `1→−1` + unit segment
   `−1→0`) as favicon + header mark; the wordmark is the formula `e^iπ+1=0`. ✅
9. **Page chrome via OOB swaps (5e).** Breadcrumbs + the Actions menu live in the fixed
   header but change per page, so fragments carry them `hx-swap-oob` (§6). ✅
10. **`about` object (5e).** The footer pages map to specific files (`README.md`,
    `LICENSE`, `vendor/README.md`) under a new `about:read` grant (reader floor); the
    files join the `content.sh` READ ACL derivation. ✅
11. **Progress is upload-replace (5e).** `GET /edit/solutions/` opens an **empty**
    buffer; the paste supersedes `.progress.html` wholesale (parse-or-reject). ✅
12. **File git status is live on deployed instances too (5e → Phase 6).** The colours
    are real everywhere, not just on a dev run. The original claim here — that they
    "degrade to plain names" because deployed uids cannot read `.git` — was wrong on
    both halves, and worth stating precisely because the mechanism is not the obvious
    one: `.git` is **world-readable** (mode `0755`), so a service uid with traverse on
    the repo root reaches it without any ACL. What actually silenced the colours is
    git's **ownership** check: it refuses a repository owned by another uid (*detected
    dubious ownership*). The query therefore carries its own `-c safe.directory=<repo>`
    — *command* scope is protected configuration, so the exception is honoured, and it
    is scoped to that one invocation rather than written into the host's git config, so
    no other uid or process gains anything. Verified: identical status output as the
    owner and under a simulated foreign owner. Still no ACL on `.git`, and this stays
    the **only** git the web tier runs — read-only `status`, no commits, no checkouts,
    no key (DD-12; the Phase-7 `euler-git` broker is what does the rest). ✅
13. **Index pages are card grids (5e)** in the §3 voice; the landing, docs index, and
    topics index share the visual system. ✅
14. **The right pane is an iframe (5e → Phase 6).** `#ws` hosts `/terminal` — a
    standalone document — so the terminal is isolated in its own browsing context
    (the old-web-server pattern): htmx swaps, content-page JS, and history restores
    cannot touch it, and its `beforeunload` guard owns the refresh/close
    confirmation (§9). Consequence: CSP `frame-ancestors` moves `'none'` → `'self'`
    (same-origin framing only; cross-origin embedding stays blocked). ✅
15. **The terminal is dark in both themes (Phase 6).** The one surface that does not
    follow the theme slider. It renders the *shell's own* output, and the shell paints
    with absolute xterm-256 indices chosen for a dark terminal (near-whites like 254/247
    for body text, 238 for rules): on a light background its banner and prompt wash out
    to illegible — observed, not assumed. Re-theming the surface without re-tuning the
    shell's palette would only break the contrast the shell already designs for. So the
    pane keeps the site's **dark** `--surface`, literally, and reads as an embedded
    console on a light page. (Re-tuning the shell's palette per theme is the alternative
    if this ever matters; it is a shell change, not a client one.) ✅
16. **The attach replay is drawn, never obeyed (Phase 6).** A (re)attaching terminal is
    sent the shell's recent scrollback — which contains the *control sequences* of
    commands that already ran, `show`/`edit`'s OSC 5379 among them. A client that acted
    on those again would hijack the pane on **every page load**: deep-link to one problem
    and land on whatever the shell last showed. So the server closes the replay with an
    explicit `{"replay":"end"}` text frame (the raw byte stream cannot carry an in-band
    marker), and the client honours OSC only after it — sequenced *through* xterm's write
    queue, since `write()` is asynchronous and the bytes are still being parsed when the
    marker arrives. The monotonic token stays as the within-session guard. ✅
