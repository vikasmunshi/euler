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
│ HEADER  eiπ+1=0 │ Solutions · Docs · Topics │ Actions ▾ │ crumbs… │ ◐ │ 🯅 ▾ │  fixed
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
  **Actions** menu (page-specific verbs, §6) · **breadcrumbs** (the current path,
  ancestors clickable) · the **theme slider** (◐, light⇄dark) · the **user glyph**
  (initial in a circle) opening a sub-menu: *Account* (`/account`, left pane),
  *Change password* (`/forgot`, auth tier), *Logout* (`POST /auth/logout`).
- **Left pane** `#content` — the navigable region. Nav and in-page links `hx-get` a
  route and swap it here; the URL updates (`hx-push-url`) so every view is
  deep-linkable. Scrolls **both axes** when content overflows.
- **Right pane** `#ws` — the PTY terminal (Phase 6). It talks only to `/ws`;
  **left-pane navigation never touches `/ws`**, so the terminal session persists
  while content swaps. Scrolls **vertically** when needed (wired in Phase 6).
- **Footer** (fixed) — © Vikas Munshi · MIT license (`/about/license`) ·
  terms of use (`/terms`) · readme (`/about/readme`) ·
  acknowledgements (`/about/acknowledgements`).

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
  font stack; vendored htmx from `/vendor`.

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
| **Auth service** (`auth.sock`) | `/login`, `/register*`, `/reset*`, `/forgot`, `/terms`, `/auth/*` | public surface + `forward_auth` gate |
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
route remains the boundary):

| Page | Actions (floor) |
|---|---|
| `/solutions/` | Upload progress (`solutions:execute`) |
| `/solutions/{n}/` | Regenerate notes (`ai:execute`) |
| `/solutions/{n}/{file}` (editable) | Edit (`solutions:write`) · Delete (`solutions:delete`, bare `.py`/`.c`) |
| `/edit/solutions/{n}/{file}` | Save (`solutions:write`) · Delete (`solutions:delete`) |
| `/edit/solutions/` | Save (`solutions:execute`) |
| elsewhere | — (the menu hides when empty) |

*Save* submits the page's editor form; *Delete* confirms, then swaps the problem
page back into `#content`. Menus (`Actions`, the user glyph) are native
`<details>` dropdowns — no JS framework, a few lines in `site.js` close them on
selection.

## 7 · Content pages

- **Landing (`/`), docs index, topics index** — visually alike: a short hero
  (kicker · title · one wry lede) over a **card grid, two/three per row** — each
  card an icon, a title, and a blurb that earns its place (§3). The landing's
  cards are the entry points (Solutions · Docs · Topics · Terminal); the docs and
  topics indexes list their pages the same way.
- **Solutions (`/solutions/`)** — the 10×10 century grids, **two grids per row**,
  cells shaded by difficulty with **per-theme heat tokens** (§2), title + pct on
  hover. Page action: **Upload progress** → `/edit/solutions/`.
- **Progress upload (`/edit/solutions/`)** — an **empty** paste buffer (this is a
  *replace*, not an edit — the previous `.progress.html` is superseded wholesale);
  parse-or-reject before anything lands, success answers with the refreshed grids.
- **Problem (`/solutions/{n}/`)** — statement first, then **test cases · results ·
  files · notes** (in that order):
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
| GET | `/` | the app shell; left pane = the **landing** (default content), right pane = ws | `web-content:read` |

### 8b — read (left-pane content) ✅

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/solutions/` | `problems.json` as **10×10 century grids** (two per row, per-theme heat) + summary | `solutions:read` |
| GET | `/solutions/{n}/` | the `solution_dir`: statement, then test-cases · results · files · notes (§7) | `solutions:read` |
| GET | `/solutions/{n}/{filename}` | one problem file (solution source, `statement.html`, `resources/*`) | `solutions:read` |
| GET | `/docs/` | docs index (card grid) | `docs:read` |
| GET | `/docs/{name}` | a rendered doc — **all** guides incl. `ai` / `convention_*` (the file may live in `docs/` or elsewhere) | `docs:read` |
| GET | `/topics/` | topics index (card grid, blog-style writeups) | `docs:read` |
| GET | `/topics/{name}` | a topic page (e.g. `prime-numbers`) | `docs:read` |
| GET | `/account` | the signed-in user + profile (from `X-User` / `X-Profile`) | `users:read` |
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
| POST | `/solutions/{n}/notes/regenerate` | AI-regenerate `notes.html` → notes block | `ai:execute` |

**Writes always return a fragment** (never the shell). The regenerate route
returns the notes block with a pointer to the shell path (`claude-api docs {n}`) —
the content tier deliberately cannot reach the Claude API (no key on the service
uid, no egress, no `ai` extra), so a real backend awaits a brokered design (Phase 6+).

### execute — via the terminal (`/ws`), Phase 6

Execution is **not** per-route POSTs; the right-pane terminal sends commands to `/ws`. The
left-pane navigation never uses `/ws`. Commands to wire (all **dummy stubs until Phase 6**):

| Command | Arg | Purpose | Intended floor |
|---|---|---|---|
| `set` | `<problem_number>` (required) | set the active problem for the session | `solutions:read` |
| `show` | — | show the active problem / its files | `solutions:read` |
| `ls` | — | list files of the active problem | `solutions:read` |
| `eval` | — | evaluate the active solution | `solutions:execute` |
| `benchmark` | — | benchmark the active solution | `solutions:execute` |

Command gating and the ws↔profile binding are finalized in Phase 6 (§7.6).

## 9 · Render & navigation contract

- **Shell vs fragment.** `/` returns the full shell. A read/edit path returns its
  `#content` fragment on `HX-Request` (plus the §6 chrome out-of-band), or the full
  shell with `#content` pre-populated on a direct visit — so links are shareable and
  reload-safe.
- **Navigation refreshes only the left pane.** Every in-app link swaps `#content`;
  the shell (header, footer, `#ws`) is never re-rendered by navigation. Only the
  auth-tier destinations (change password, logout, terms) leave the shell.
- **Canonical trailing slash.** Every GET path is canonical *with* its trailing slash
  (`/solutions/`, `/docs/`, `/topics/`, `/solutions/{n}/`, `/edit/solutions/`). A GET
  missing the slash → **301** redirect to the slashed form, so each view has one URL.
- **Terminal persistence.** htmx swaps only `#content`; `#ws` (the terminal) is untouched
  by navigation and keeps its session.
- **Nav (fixed header):** brand → `/`, `Solutions` → `/solutions/`, `Docs` → `/docs/`,
  `Topics` → `/topics/`, user glyph → account/password/logout. Profile-gated
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
6. **Execute via `/ws`** with `set`/`show`/`ls`/`eval`/`benchmark`; dummy until Phase 6,
   where ws gating (`shell:execute` is admin-only vs the web maintainer cap) is resolved. ⬜
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
12. **File git status is best-effort (5e).** The web tier stays git-less (DD-12): the
    colours appear only where `.git` is readable (dev/owner runs); deployed instances
    degrade to plain names. No ACL on `.git` — history and the key path stay off the
    web tier. ✅
13. **Index pages are card grids (5e)** in the §3 voice; the landing, docs index, and
    topics index share the visual system. ✅
