# Content-service site map

The URL surface of the content service (`solver/web/site`), and the authority the
view/edit sub-steps (Phase 5b–5d) implement against. Every route is gated by an
`object:permission` capability checked against the request's `X-Profile`
([DD-12](secure-web-server.md#dd-12--unified-authorization-solverauth--authorizationsjson)),
and renders either a **full page** or a **named block** of the same template on
`HX-Request` ([DD-10](secure-web-server.md#dd-10--phase-5-content-service-choices),
[§4.5](secure-web-server.md)).

> **Status.** 5a routes (chrome) live; 5b (view) / 5c (validation) / 5d (edit) below are
> the plan. This doc is the contract they build to.

## 1 · Path ownership

One host, one authenticated origin; paths are split across tiers by Caddy
([frontend.sh](../scripts/setup/frontend.sh)). The content service owns only the
authenticated catch-all — it must not mint a path that collides with a reserved one.

| Owner | Paths | Notes |
|---|---|---|
| **Caddy-native / static** | `/healthz`, `/assets/*`, `/vendor/*`, `/favicon.ico` | served from `/etc/euler/web-content`; same-origin so CSP `'self'` holds |
| **Auth service** (`auth.sock`) | `/login`, `/register*`, `/reset*`, `/forgot`, `/terms`, `/auth/*` | public surface + `forward_auth` gate ([DD-7](secure-web-server.md)) |
| **ws service** (`ws-<profile>.sock`, Phase 6) | `/ws` | PTY WebSocket; the `/shell` page is served by content, the socket by ws |
| **Content service** (`content-<profile>.sock`) | everything else below | per-profile instance, chosen by Caddy on `X-Profile` |

## 2 · Capability → profile floor

The web ladder caps at `maintainer` (`admin` is local-only,
[DD-11](secure-web-server.md#dd-11--profiles--content-service-access)). Floors below are
the lowest profile that inherits the grant.

| Capability | Floor | Backs |
|---|---|---|
| `web-content:read` | reader | the site chrome (home, nav, shell page) |
| `docs:read` | reader | rendered guides + composed reference pages |
| `solutions:read` | reader | summary, problem detail, solution/statement files |
| `solutions:execute` | contributor | eval / benchmark a solution |
| `solutions:write` | contributor | editor, save, lint |
| `solutions:delete` | maintainer | delete a solution file |
| `ai:execute` | maintainer | regenerate notes |
| `progress:write` | maintainer | edit the shared progress page (**new grant**, §5.3) |
| `users:read` | reader | own-account page |

An unauthenticated caller (no `X-Profile`, i.e. bypassed Caddy) → **401**; an
authenticated caller lacking the grant → **403**. A per-profile instance also refuses a
mismatched `X-Profile` (401) — the `EULER_PROFILE` pin.

## 3 · Route table

`Block` = the `{% block %}` returned on `HX-Request` (else the whole page). Writes always
return a fragment. `⟵` marks a route the `show`/`edit` shell commands already target, so
its shape is **fixed** (`core/viewer.py`: `/NNNN/`, `/edit/NNNN/<file>`).

### 3a · Chrome — Phase 5a ✅

| Method | Path | Template · block | Requires | Phase |
|---|---|---|---|---|
| GET | `/` | `home.html` · `main` | `web-content:read` | 5a ✅ |
| GET | `/shell` | `shell.html` · `main` (Phase-6 panel stands in) | `web-content:read` | 5a ✅ |

### 3b · View — Phase 5b

| Method | Path | Renders | Requires | Notes |
|---|---|---|---|---|
| GET | `/summary` | progress dashboard (`.progress.html` → `problems.json`, `utils/summary.py`) | `solutions:read` | landing target for "my progress" |
| GET | `/active-problem` | `302 → /{last}/` | `solutions:read` | the user's last active problem |
| GET | `/{n}` | `301 → /{n}/` | `solutions:read` | canonical trailing slash |
| GET | `/{n}/` ⟵ | problem detail: `statement.html` + `notes.html` + solution list + `results.json` | `solutions:read` | one page composes the problem |
| GET | `/{n}/{file}` | a raw problem file (solution source, `statement.html`, `resources/*`) | `solutions:read` | read from `problem.solution_dir` (incl. decrypted `private`) |
| GET | `/docs` (`/index`) | guides index | `docs:read` | left-pane default |
| GET | `/docs/{name}` | a rendered `docs/*.md` guide | `docs:read` | e.g. `user-guide`, `syntax` |
| GET | `/ai/{name}` | a composed reference page (the `convention_*.md` set) | `docs:read` | read-only; generation is shell-only |
| GET | `/account` | the signed-in user + profile (from `X-User`/`X-Profile`) | `users:read` | the profile pill links here |

### 3c · Validation — Phase 5c

Not routes — the **save gate** every 5d write passes through: `.py` (flake8 + autofix),
`.c`, `.json` reject-and-restore, and the **`.html` gate via nh3** (sanitize-and-store-clean,
[DD-10](secure-web-server.md#dd-10--phase-5-content-service-choices); `notes.html` is served
back and rendered, so unsanitised HTML is stored-XSS). `nh3` is not yet installed.

### 3d · Edit — Phase 5d (each write → 5c, each response carries CSP)

| Method | Path | Renders | Requires | Notes |
|---|---|---|---|---|
| GET | `/edit/{n}/{file}` ⟵ | code-editor page | `solutions:write` | |
| POST | `/edit/{n}/{file}` ⟵ | save → editor block + status toast | `solutions:write` | via 5c gate |
| DELETE | `/edit/{n}/{file}` ⟵ | delete → updated file-list block | `solutions:delete` | maintainer only |
| POST | `/edit/lint` | stateless lint result (suffix-keyed) | `solutions:write` | no write; editor affordance |
| POST | `/{n}/cmd` | eval / benchmark → result fragment (benchmark progress via **SSE**) | `solutions:execute` | runs the solution |
| GET · POST | `/edit/progress` | progress-page editor / save | `progress:write` (maintainer) | rewrites the shared `.progress.html`; new grant, §5.3 |
| POST | `/{n}/notes/regenerate` | AI-regenerate `notes.html` → notes block | `ai:execute` | maintainer |

## 4 · Navigation

```
header nav (every page):  Home /   ·   Summary /summary   ·   Guides /docs   ·   Shell /shell   ·   [profile pill]
  Summary ──problem link──▶ /{n}/
  /{n}/  ──▶ /{n}/{file} (view source)   ──▶ /edit/{n}/{file} (contributor+)   ──▶ eval/benchmark POST /{n}/cmd (contributor+)
  /docs  ──▶ /docs/{name}   ·   /ai/{name}
```

Profile-gated affordances are **omitted from the nav for profiles that lack them** (a
reader sees no Edit link), and the route still enforces the gate server-side — nav hiding
is UX, the `requires()` check is the boundary.

## 5 · Decisions

1. **URL scheme.** Keep the legacy paths (`/{n}/`, `/edit/{n}/{file}`, `/docs/{name}`,
   `/summary`, `/ai/{name}`) — required for `show`/`edit` compatibility. ✅
2. **eval/benchmark floor** = `solutions:execute` (contributor). ✅
3. **`/edit/progress` floor** = **maintainer**, via a new `progress:write` grant
   (`objects.progress` → `["solutions/.progress.html"]`, granted to `maintainer`). Added to
   `authorizations.json` in 5d; its ACL follows the existing `solutions/` write ACL. ✅
4. **Optional routes** — **both included**: `/account` (`users:read`) in 5b, and
   `/{n}/notes/regenerate` (`ai:execute`, maintainer) in 5d. ✅
5. **Web-shell gating** (Phase 6, `/shell` + `/ws`): `shell:execute` is admin-only but web
   caps at maintainer — needs a dedicated web-shell capability or a maintainer cap. Deferred
   to Phase 6. ⬜
