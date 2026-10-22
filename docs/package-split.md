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
| Q4 | Role source | The root-owned policy when present; otherwise the owner of the install is `admin`. Signed grants only if a need appears. The policy is the existing `/etc/euler/authorizations.json` (root-owned, already keyed by e-mail *or* OS login) rather than a new `roles.json`. |
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
  packages/solver/solver/    euler-solver    import solver          shell, core, crypto, ai, runners, templates, utils, config, auth (login/role)
  site/      euler-site      import euler_site      site app, auth service, cache/csp/store/unixhttp/envfile, env.conf, static assets
  webshell/  euler-webshell  import euler_webshell  ws, per-user service, msg, osc, overlays, ticket identity, roster, `users`, key distribution
content/     euler-content   data-only wheel: docs, topics, README, public solutions, problems.json
```

Dependencies point one way: `euler_webshell → euler_site → solver` (the site uses solver's
*domain* modules — problems, the progress parser, paths — never the shell). The layering
checker (`scripts/linters/layers.py`) enforces it.

### 3.2 Extension: explicit composition

`solver.main.main(argv, *, extension=None)`. The web shell's entry point passes an
`Extension` (`packages/solver/solver/shell/extension.py`) carrying extra command modules, an overlay table
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

`packages/solver/solver/shell/login.py`, run by `main()` at startup:

1. **Who and role** — `identify()`, before any command module loads (each command's floor
   is checked as it registers). The solver shell's own is the OS login — the real uid's
   account name, never `$USER` — with the Q4 chain (`packages/solver/solver/auth/identity.py`): the
   root-owned policy's entry for the login; else the e-mail whose `system_slug` *is* the
   login (a per-user web uid, so a `solver` run inside a web shell holds its owner's rung);
   else `reader`. No policy → the checkout owner is `admin`, anyone else `contributor`. A
   policy counts only if it and every directory above it are root-owned. An `Extension` may
   bring its own identity: the web shell redeems its one-time ticket
   (`packages/webshell/euler_webshell/shell/identity.py`).
2. **Vault** — `unlock()`: `EULER_VAULT_KEY_FILE` → `EULER_VAULT_PASSWORD` → a terminal
   prompt, unless the extension says `prompt_vault=False` (the web shell: the browser
   unlocks). The vault's state is read where it matters (the key file), not copied onto the
   `Subject`.

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
| 6 | Physical move to `packages/`, three pyprojects, import renames, units, Makefile/hooks/tests, lockstep release | install, audit, pre-push, `upgrade-web` pass |
| 7 | Resource-side enforcement for admin/maintainer commands; terminal vs web catalogues; docs | Audit table recorded ✓ |

## 5. Progress

- **Phase 0–1** (`32066ade2`): this document; `scripts/linters/layers.py` + `layers.allow`;
  `packages/solver/solver/shell/extension.py` and `main(extension=)`.
- **Phase 2**: OSC lives in `packages/webshell/euler_webshell/shell/` (the future `euler_webshell`): `osc.py`
  (moved from `packages/solver/solver/core/`, plus `nudge`), `overlays.toml`, `viewer.py` (the pane-swapping
  `show` / `edit`), and the entry point `python -m euler_webshell.shell`, which the per-user
  service's PTY now runs. The solver's `show` / `edit` only open a browser tab, and
  `git` / `summary` / `keys` emit nothing. The message commands, web-side themselves, emit
  directly — including the git nudge after `msg act` saves a key or merges a request.
  - *Coarser nudges, as designed:* an overlay fires after the command whatever happened
    (e.g. `gh-merge` nudges the message chip even when no notice was dismissed). Each is a
    cheap re-read.
  - *Nested shells:* a `solver …` run from inside the web shell (`!`, `claude-solve`) is a
    plain solver shell: it sends no OSC (previously it did, and Claude's captured output
    carried the escapes) and its `show` looks for a local browser.

- **Phase 3**: `login` (`packages/solver/solver/shell/login.py`) settles identity before commands load and
  the vault after; `Extension` gained `identity`, `prompt_vault` and `on_start`. `solver.auth`
  is the OS login plus the Q4 role chain only; the ticket plane is
  `packages/webshell/euler_webshell/shell/identity.py`. The instance-identity plane (`EULER_USER_EMAIL` handed
  down to child `solver` processes) is gone: a child is a plain solver shell, and the policy
  maps its per-user uid back to its owner's e-mail and rung. The web shell's quiet start-up
  `git-sync` is its `on_start` hook.
  - *Tightened:* the login is read from the uid, not `$USER`; an `EULER_AUTHZ_FILE` the
    user can write is ignored; with a policy deployed, an unlisted checkout owner is
    `reader`, not `admin`; an infra `euler-*` uid gets `reader` instead of aborting.
  - *Still in solver, for phase 4:* `packages/solver/solver/core/git.py` `key_waiting_hint` words its hint
    by channel.

- **Phase 4**: `layers.allow` is empty — the solver shell imports no web code.
  - *Notices:* `packages/solver/solver/core/notices.py` is the escape hatch § 3.2 kept for what an overlay
    cannot express — a notice whose text depends on what the command found (`git-push`'s
    pull request, `summary`'s unregistered answers, `user`'s key request, the merge that
    dismisses a review notice). Solver commands file through it; an `Extension` installs the
    carrier (`packages/webshell/euler_webshell/shell/notices.py`, the spool). With none, nothing is sent and each
    caller says what to do by hand. The subjects live there too, and `euler_webshell.msg`
    re-exports them. The waiting-key hint is the carrier's wording, so no channel check
    remains in solver.
  - *Key distribution (Q1):* `user-authorize`, `key-split` and `host-authorize` moved to
    `packages/webshell/euler_webshell/shell/keys.py`; `key-rekey`'s re-issue to the roster is an overlay `replace`
    there. The solver keeps holding and receiving — `user`, `vault`, `key-reconstruct`,
    `host-unlock`, a local `key-rekey` — and gains `key-export`, which prints the sealed
    block `host-unlock` takes: the file-based issue Q1 promised.
  - *Command modules:* `msg`, `users` and the key commands load through the extension's
    `modules`, not `modules.csv` (the loader marks `packages/site/euler_site` rows non-registering until
    phase 6 moves the tree out). Hence **`solver-host`** (`python -m euler_webshell.shell.host`):
    the solver shell plus those commands and the spool, with the OS login and a terminal
    vault prompt, for the operator on the host.
  - *Docs:* while the catalogue is one (phase 7 splits it), `update-docs` must see every
    command, so it refuses in a plain `solver` when the web shell is installed;
    `check-commands` in `check.sh` runs under the host shell too.
  - *Lost, as accepted:* a plain `solver` run inside a web shell (`! solver "git-push"`)
    files no notice — it has no carrier. The web shell's own `git-push` does.

- **Phase 5**: signed-out browsing.
  - *Content package:* `content/` is the `euler-content` source (`pyproject.toml`,
    `euler_content/__init__.py` with `root()`); `scripts/content/stage.py` stages it with
    the public tree — tracked files only, under fixed public roots, refusing
    `solutions/private` — and the version stamped from `packages/solver/solver/version.py`. `venv.sh`
    installs it into `/opt/euler` on every venv deploy, so `redeploy-web` refreshes it.
  - *ContentRoot:* rather than a class, the two roots are the two ways the one app is
    built — `build_public_app` on the packaged tree (`SiteConfig.public`, read routes
    only, no identity middleware, no git) and the per-user service on the clone. The
    content readers keep taking a root directory; the packaged tree mirrors the repo's
    layout, so they need no second code path.
  - *Service and edge:* `scripts/setup/site.sh` (`euler-site`, `/run/euler/site.sock`,
    `ProtectHome=true`, AF_UNIX only) with `make deploy-site` etc., in the `*-web`
    aggregates; `frontend.sh` routes content GETs without a session cookie to it.
  - *Templates:* `browsable` (navigation live) is split from `subject` (what is yours);
    the public right pane is a sign-in card. The auth tier's signed-out pages now link
    into the public site instead of wearing padlocks.
  - *Not done:* public responses are still `no-store` — positive caching needs versioned
    URLs (web-server-guide § Caching) — and the crawl found 20 broken links that the
    signed-in site has too (topics not yet written, statement-relative PE links).

- **Phase 6**: the physical split.
  - *Layout:* `packages/solver/solver` (euler-solver), `packages/site/euler_site` (euler-site:
    the site app as `euler_site.site`, the auth service as `euler_site.auth`, the shared
    `cache`/`csp`/`store`/`unixhttp`/`envfile`, the auth `templates/` and the static
    `content/`), `packages/webshell/euler_webshell` (euler-webshell: `ws`, `user`, `msg`,
    `shell`, `roster`, and `users` — the `users` command, formerly `solver.web.auth.commands`).
    The old `solver.web.X` became `euler_site.X` or `euler_webshell.X` one for one, so every
    `python -m` entry point keeps its shape.
  - *Packaging:* one pyproject per package; the root `pyproject.toml` is no package any more
    (it keeps the system-setup notes). euler-site pins `euler-solver==X.Y.Z` and
    euler-webshell pins both; `scripts/version/release.sh` writes the three version.py and
    the pins together. A dev venv and `/opt/euler` install all three at once
    (`make install-all`, `venv.sh`), after removing the old single `solver` distribution.
  - *Paths:* the checkout-relative paths the code reads (`values.conf`, the runner header,
    the templates and skills the docs link, `home-summary.md`, the static tree Caddy deploys)
    follow the move; `solver.config.paths.PACKAGE_DIR` names the solver's place in the tree.
    The loader names modules from the package's parent, so `modules.csv` lists only `solver.*`.
  - *Guards:* `layers.py` checks all three layers (`euler_webshell → euler_site → solver`);
    the hooks and `check.sh` lint `packages`; `update-docs` renders one layout tree per
    package; `git-publish`'s code scope is `packages`.
  - *Deploying it:* the units name new modules (`-m euler_site.auth`, `-m euler_webshell.msg`,
    …), so this release needs `make upgrade-web` (re-lays every unit), not `redeploy-web`.
    Collaborators' clones pick up the layout at their next `git-sync`; until then, the few
    pages that read the clone's `solver/` files (the AI doc, the template links) 404.

- **Phase 7**: the audit, the catalogues, the docs. The split is complete.
  - *Enforcement audit:* `docs/authorizations.md` § Where it is enforced — every
    `maintainer` / `admin` command, what it changes, and the boundary that actually decides
    (own clone + GitHub's locked `master`, the master key, sudo, the spool's `SO_PEERCRED`
    check, the `euler-maint` group, the relay firewall). No command relies on its floor
    alone; no gap needed fixing. `tests/test_enforcement_audit.py` holds the table to the
    live registry, so a new privileged command fails until it is audited.
  - *Catalogues:* the generated catalogue is two tables — every shell, and the web host only
    (the web shell and `solver-host`) — and the command index marks the web-host-only
    entries. A generated table lists what the web shell's overlays change.
  - *Docs:* the developer guide's § 9 (three packages, extensions, notices, which shell has
    which command) and its checklist; the user guide's web section (public pages, the web
    shell, `solver-host`).
