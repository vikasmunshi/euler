# Content-service site design

The layout, visual identity, and URL surface of the content service
(`solver/web/site`) — the contract the view/edit sub-steps (Phase 5b–5d) build to.
The site is **one server-rendered app shell**: a persistent frame whose content pane is
swapped by **htmx** fragments, never a client-side SPA. Every route is gated by an
`object:permission` capability checked against the request's `X-Profile`
([DD-12](secure-web-server.md#dd-12--unified-authorization-solverauth--authorizationsjson))
and every response carries the per-response CSP nonce
([§4.7](secure-web-server.md), [DD-10](secure-web-server.md#dd-10--phase-5-content-service-choices)).

> **Status.** 5a shell live (to be revised to the four-region layout below); 5b (view) /
> 5c (validation) / 5d (edit) are the plan.

## 1 · The app shell — four regions

`GET /` serves `home.html`, the whole shell; every other path renders **into a region of
it**. Two regions are fixed anchors, two are variable-length content:

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER   ς euler   Solutions · Docs · Topics        [pill]   │  fixed
├───────────────────────────────┬─────────────────────────────┤
│  LEFT PANE  (#content)         │  RIGHT PANE  (#ws)           │
│  navigable content, htmx-      │  the solver PTY terminal     │  variable
│  swapped; deep-linkable        │  over /ws (Phase 6)          │
│                                │  persists across left swaps  │
├───────────────────────────────┴─────────────────────────────┤
│  FOOTER                                                       │  fixed
└─────────────────────────────────────────────────────────────┘
```

- **Header** (fixed) — the brand `ς euler`, primary nav (Solutions · Docs · Topics), and
  the account pill. **Buttons and glyphs keep the same position on every page** — the
  header is a stable control surface, not content.
- **Left pane** `#content` — the navigable region. Nav and in-page links `hx-get` a route
  and swap it here; the URL updates (`hx-push-url`) so every view is deep-linkable.
- **Right pane** `#ws` — the PTY terminal (Phase 6). It talks only to `/ws`; **left-pane
  navigation never touches `/ws`**, so the terminal session persists while content swaps.
- **Footer** (fixed).

**Layout principle.** Fixed header + footer bracket the page; all variable-length content
lives in the two middle panes (left = documents/views, right = terminal). Controls never
move between pages.

## 2 · Visual identity & theme

- **Symbol** — `ς` (Greek small letter **final** sigma, U+03C2), the site glyph: the
  header brand (`ς euler`) and the favicon. (Not the summation `Σ`.)
- **Theme — dark-first.** The dark palette is the primary design; light is offered via
  `prefers-color-scheme` and a `data-theme` toggle. Accent is a warm orange, carried
  through the symbol, links, and focus rings.

  | token | dark (primary) | light |
  |---|---|---|
  | `--bg` | `#0f1115` | `#f7f7f8` |
  | `--surface` | `#171a21` | `#ffffff` |
  | `--border` | `#2a2f3a` | `#e5e7eb` |
  | `--text` | `#e5e7eb` | `#1f2937` |
  | `--muted` | `#9ca3af` | `#6b7280` |
  | `--accent` | `#f97316` | `#f97316` |

- Self-contained + same-origin only (CSP `'self'`): no external fonts/CDNs; system font
  stack; vendored htmx from `/vendor`.

## 3 · Path ownership

One host, one authenticated origin; Caddy splits paths across tiers
([frontend.sh](../scripts/setup/frontend.sh)). The content service owns only the
authenticated catch-all and must not collide with a reserved path.

| Owner | Paths | Notes |
|---|---|---|
| **Caddy-native / static** | `/healthz`, `/assets/*`, `/vendor/*`, `/favicon.ico` | served from `/etc/euler/web-content`; same-origin |
| **Auth service** (`auth.sock`) | `/login`, `/register*`, `/reset*`, `/forgot`, `/terms`, `/auth/*` | public surface + `forward_auth` gate |
| **ws service** (`ws-<profile>.sock`, Phase 6) | `/ws` | PTY WebSocket; the right pane connects here |
| **Content service** (`content-<profile>.sock`) | everything else below | per-profile instance, chosen on `X-Profile` |

## 4 · Capability → profile floor

The web ladder caps at `maintainer` (`admin` is local-only,
[DD-11](secure-web-server.md#dd-11--profiles--content-service-access)).

| Capability | Floor | Backs |
|---|---|---|
| `web-content:read` | reader | the app shell (header/footer/panes) |
| `docs:read` | reader | guides, composed reference pages, topics |
| `solutions:read` | reader | the solutions grid, problem pages, files |
| `solutions:execute` | contributor | `eval` / `benchmark` (via `/ws`); the progress editor |
| `solutions:write` | contributor | editor, save, lint |
| `solutions:delete` | maintainer | delete a solution file |
| `ai:execute` | maintainer | regenerate notes |
| `users:read` | reader | the account page |

No-subject (bypassed Caddy) → **401**; authenticated but lacking the grant → **403**; a
per-profile instance also refuses a mismatched `X-Profile` (401 — the `EULER_PROFILE` pin).

## 5 · Routes

`Fragment` = what an `hx-get`/`hx-post` from the shell renders into `#content` (or `#ws`);
a **direct** hit on the same path returns the whole shell with that pane pre-populated
(deep-link). Writes always return a fragment.

### 5a — shell ✅ *(revise to §1's four-region layout + ς + dark-first)*

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/` | the app shell; left pane = the **landing** (default content), right pane = ws | `web-content:read` |

### 5b — read (left-pane content)

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/solutions/` | `problems.json` as **10×10 century grids** (solved/level heat) + summary info | `solutions:read` |
| GET | `/solutions/{n}/` | the `solution_dir`: number, title, level, statement, topics, files, test-cases, results, notes | `solutions:read` |
| GET | `/solutions/{n}/{filename}` | one problem file (solution source, `statement.html`, `resources/*`) | `solutions:read` |
| GET | `/docs/` | docs index | `docs:read` |
| GET | `/docs/{name}` | a rendered doc — **all** guides incl. `ai` / `convention_*` (the file may live in `docs/` or elsewhere) | `docs:read` |
| GET | `/topics/` | topics index (blog-style writeups) | `docs:read` |
| GET | `/topics/{name}` | a topic page (e.g. `prime-numbers`, `graph-theory`, `number-theory`) | `docs:read` |
| GET | `/account` | the signed-in user + profile (from `X-User` / `X-Profile`) | `users:read` |

### 5c — validation (the save gate)

Not routes — the checks every 5d write passes: `.py` (flake8 + autofix), `.c`, `.json`
reject-and-restore, and the **`.html` gate via nh3** (sanitize-and-store-clean — `notes.html`
is served back and rendered, so raw HTML is stored-XSS;
[DD-10](secure-web-server.md#dd-10--phase-5-content-service-choices)). `nh3` not yet installed.

### 5d — edit (each write → 5c; each response carries CSP)

| Method | Path | Renders | Requires |
|---|---|---|---|
| GET | `/edit/solutions/` | the **progress editor** (collection-level; no problem number) | `solutions:execute` |
| POST | `/edit/solutions/` | save progress → grid block + status (writes `solutions/.progress.html`) | `solutions:execute` |
| GET | `/edit/solutions/{n}/{filename}` | code-editor for the file | `solutions:write` |
| POST | `/edit/solutions/{n}/{filename}` | save → editor block + status | `solutions:write` |
| DELETE | `/edit/solutions/{n}/{filename}` | delete → updated file-list block | `solutions:delete` |
| POST | `/{n}/notes/regenerate` | AI-regenerate `notes.html` → notes block | `ai:execute` |

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

## 6 · Render & navigation contract

- **Shell vs fragment.** `/` returns the full shell. A read/edit path returns its
  `#content` fragment on `HX-Request`, or the full shell with `#content` pre-populated on a
  direct visit — so links are shareable and reload-safe.
- **Canonical trailing slash.** Every GET path is canonical *with* its trailing slash
  (`/solutions/`, `/docs/`, `/topics/`, `/solutions/{n}/`, `/edit/solutions/`). A GET
  missing the slash → **301** redirect to the slashed form, so each view has one URL.
- **Terminal persistence.** htmx swaps only `#content`; `#ws` (the terminal) is untouched
  by navigation and keeps its session.
- **Nav (fixed header):** brand `ς` → `/`, `Solutions` → `/solutions/`, `Docs` → `/docs/`,
  `Topics` → `/topics/`, account pill → `/account`. Profile-gated affordances (Edit,
  delete) are hidden from profiles that lack them; the route still enforces the gate
  server-side — nav hiding is UX, `requires()` is the boundary.

## 7 · Decisions & consequences

1. **App-shell layout** — one page `/`, four regions (§1); content is htmx fragments into
   `#content`, terminal in `#ws`. 5a's current single-column shell is revised to this. ✅
2. **URL scheme under `/solutions/`** (`/solutions/{n}/`, `/edit/solutions/{n}/{filename}`).
   **`core/viewer.py` must be updated** — `show` → `/solutions/NNNN/`, `edit` →
   `/edit/solutions/NNNN/<file>` (it currently emits `/NNNN/` and `/edit/NNNN/<file>`). ⬜
3. **Folded away:** `/summary` → the `/solutions/` century grids; `/ai/{name}` →
   `/docs/{name}`; `/{n}/cmd` → the `/ws` command set. The **progress editor** returns as
   the collection-level `/edit/solutions/` (GET/POST, no DELETE), gated `solutions:execute`
   — contributor-floored, so the existing `euler-sol-write` ACL already covers its write to
   `solutions/.progress.html`: no `progress:write` grant and no new ACL. ✅
4. **`topics/` is a new content tree** (blog-style). It joins the `euler-sol-read` content
   ACL (add `topics/` to `content.sh`'s read paths) and is gated `docs:read`. A problem's
   `topics` field is **new data** — needs a per-problem tagging source. ⬜
5. **Data:** `level` / `pct` / `solved` / `date` come from `problems.json` today; `topics`
   does not (see 4). Difficulty renders from `Problem.difficulty`.
6. **Execute via `/ws`** with `set`/`show`/`ls`/`eval`/`benchmark`; dummy until Phase 6,
   where ws gating (`shell:execute` is admin-only vs the web maintainer cap) is resolved. ⬜
