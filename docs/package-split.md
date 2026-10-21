# Package split — design of record

The application is being split into three independently installable packages: the
**solver shell**, the **content site**, and the **web shell**. This document records the
decisions and the plan; it is updated as each phase lands.

## 1. Goals

- Clean separation between the solver shell, the content website and the solver web shell.
- One package folder (with its own `pyproject.toml`) per part.
- The solver shell works on its own: no web code, no OSC, no ticket identity.
- The web shell **imports and extends** the solver package. A config file of *overlays*
  adds OSC emits to registered commands and, where needed, replaces a command's body.
- The content site serves **unauthenticated** visitors from a packaged copy of the public
  content (docs, topics, public solutions are published unencrypted on GitHub anyway) and
  **authenticated** collaborators from their own clone.
- Identity in the solver shell is the OS login; the vault unlocks from the environment or a
  prompt; role comes from a source the user cannot rewrite. A `login` step owns all three.

## 2. Decisions

| # | Question | Decision |
|---|---|---|
| Q1 | Key distribution over the message spool / mail (`user-authorize`, `host-authorize`, key sharing) | Moves to the web-shell package. The standalone solver keeps the local key commands; keys travel by file export/import there. |
| Q2 | Where the auth and msg services live | `auth` → site package (it owns public vs authenticated). `msg` → web-shell package. Three packages. |
| Q3 | Freshness of public content | Packaged, as a separate data-only `euler-content` wheel, so content and code version independently. |
| Q4 | Role source | `/etc/euler/roles.json` (root-owned) when present; otherwise the owner of the install is `admin`. Signed grants only if a need appears. |
| Q5 | Versioning | Lockstep: one version, one tag; `release.sh` writes every package's `version.py`, and the web shell pins `euler-solver==X.Y.Z`. |

### 2.1 Why role is a guardrail, not a boundary

Within one uid, where the user can edit their clone, run `!` bash or call Python directly,
no in-process role check can stop them. Two options that were considered fail for this
reason or a narrower one:

- *A root-owned file in `~/.euler/`*: unlink and rename are governed by the **directory's**
  permissions. The user owns `~/.euler`, so they can move the file (or a root-owned subfolder)
  aside and put their own in its place. A tamper-proof file must live under a root-owned
  path — `/etc/euler/…`.
- *An HMAC of the role in an env var*: verifying an HMAC needs the secret in the verifying
  process, and whoever holds the secret can mint. A token would need a **signature**
  (Ed25519, public key root-owned) instead.

So the shell's role prevents accidents and shapes the command set. The real boundaries are
uids and file permissions, separate-uid services checking `SO_PEERCRED`, the vault/master
key, and GitHub branch protection. Each admin/maintainer command's *effect* is enforced
where it lands (phase 7 audit).

### 2.2 The vault is a capability, not an identity proof

Unlocking proves possession of the vault password; the uid already established who the user
is. What unlocking *grants* is the master key (private solutions) and the API key, so the
`Subject` records `vault_unlocked` and commands that need it say so.

## 3. Design

### 3.1 Packages

```
packages/
  solver/    euler-solver    import solver          shell, core, crypto, ai, runners, templates, utils, config, auth (login/role)
  site/      euler-site      import euler_site      site app, auth service, cache/csp/store/unixhttp/envfile, env.conf, static assets
  webshell/  euler-webshell  import euler_webshell  ws, per-user service, msg, osc, overlays, ticket/instance identity, roster, `users`, key distribution
content/     euler-content   data-only wheel: docs, topics, README, public solutions, problems.json
```

Dependencies point one way: `euler_webshell → euler_site → solver` (the site uses solver's
*domain* modules — problems, the progress parser, paths — never the shell). The layering
checker (`scripts/linters/layers.py`) enforces it.

### 3.2 Extension: explicit composition

`solver.main.main(argv, *, extension=None)`. The web shell's entry point passes an
`Extension` (`solver/shell/extension.py`) carrying extra command modules, an overlay table
and a `notify` callback. Plugin discovery via `entry_points` is deliberately avoided: an
editable dev venv with every package installed would load web commands into the terminal.

Overlays (`overlays.toml` in the web-shell package):

```toml
[git-pull]
emit = ["git"]                              # notify(event) after the command returns
[show]
replace = "euler_webshell.viewer:show"      # body replaced; signature must match
```

- `emit` runs after the command whatever its exit code — every event is an idempotent
  "re-read" nudge, and a failed command may still have changed state.
- `replace` must have exactly the original's `inspect.signature`, and an overlay must name
  a command that exists; otherwise the shell refuses to start, so the two sides cannot
  drift apart silently.
- A post-command emit is coarser than today's mid-command emits (a long command updates the
  chip at its end). If a case appears that a wrapper cannot express, a neutral domain hook
  is the escape hatch — not before.

### 3.3 `login`

Runs at startup before any command; produces `Subject(user, slug, channel, role,
vault_unlocked)`:

1. **Who** — an `IdentityProvider`: solver ships `OsLogin`; the web shell supplies the
   shell-ticket and instance providers.
2. **Vault** — `EULER_VAULT_KEY_FILE` → `EULER_VAULT_PASSWORD` → terminal prompt.
3. **Role** — the Q4 chain; a web-shell role comes from ticket redemption.

### 3.4 Content site: one app, two content roots

`ContentRoot` with `PackagedContent` (the `euler-content` wheel via `importlib.resources`)
and `CloneContent(~/euler)`. **Public**: one unprivileged `euler-site` service, no git, no
write routes, publicly cacheable, behind a Caddy route without `forward_auth`; it physically
lacks `solutions/private`. **Authenticated**: the per-user service mounts the same app on
`CloneContent`, adding edit routes, the git and message chips, and `/ws`.

## 4. Plan

| Phase | Work | Done when |
|---|---|---|
| 0 | This document | — |
| 1 | Layering checker with an allowlist of today's violations; `main(extension=)`; overlays (`registry` replace/wrap, signature check) | Checker in hooks + `check.sh` |
| 2 | OSC out of solver: emits deleted from git/summary/keys, `viewer` split, `osc.py` to web | No OSC under solver |
| 3 | `login` + identity/role providers; ticket/instance planes out; `roles.json` | `solver.auth` imports no web code |
| 4 | Key distribution and staff notices to the web side | Allowlist empty |
| 5 | `ContentRoot`, `euler-content`, public `euler-site` unit, Caddy public route | Signed-out browsing works; private unreachable |
| 6 | Physical move to `packages/`, three pyprojects, import renames, units, Makefile/hooks/tests, lockstep release | install, audit, pre-push, `redeploy-web` pass |
| 7 | Resource-side enforcement for admin/maintainer commands; terminal vs web catalogues; docs | Audit table recorded |
