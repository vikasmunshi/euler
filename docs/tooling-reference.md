# Tooling Reference — every make target and every script

This reference lists the repository's **tooling**: each `make` target and each script under
[`scripts/`](../scripts/), with one line on what it does. Both lists are **generated** by the
`update-docs` command from the files themselves, so they cannot drift. To change a line here,
change its source and re-run `update-docs` (from `solver-host`, docs/package-guide.md § 3.4).

The short version, for when that is all you need:

| I want to… | do this |
| --- | --- |
| set up a development machine | `make install-all` |
| ship a change to the web host | `make release` → `make redeploy-web` (docs/web-server-guide.md § 15.2) |
| check the whole web stack | `make status-web` |
| document a new make target | write a `## ` line right above it |
| document a new script | make its first header comment line, under the shebang, its summary |

---

## 1. Conventions

**Verbs.** A target's verb names the kind of thing it changes, and always matches the action
its script takes:

- **local**: what the terminal solver needs (apt packages, the `.venv`, git hooks,
  completions, Chrome, Claude Code, Node.js). The verbs are `install` / `uninstall`.
- **system**: what the web stack needs (root's systemd, the `euler-*` identities,
  `/etc/euler`, `/opt/euler`). The verbs are `deploy` / `remove` / `redeploy`, plus `upgrade` on the
  kits where it differs from `deploy` (docs/web-server-guide.md § 15.2).

Every **system** target needs `sudo`, and so does `status-web`, although it only reads.

**Kits.** Each web component has one script in `scripts/setup/`, its *kit*, taking an action word
(`deploy`, `remove`, `status`, …). The `make` targets are thin wrappers over those actions, and the
`-web` targets chain them in dependency order.

**Summaries.** A target's line below is its `## ` comment in the
[`Makefile`](../Makefile), and the table it sits in is the `# ── <title> ──` section it falls
under. A script's line is its summary: a Python script's docstring line, or a shell
script's first header comment under the shebang. Every target and every script must have one;
`tests/test_update_doc.py` fails on any that does not.

**Completion.** Every shell script that is run directly has bash tab-completion for its actions,
flags and arguments ([`scripts/bash_completions.sh`](../scripts/bash_completions.sh), installed
by `make install-completions`). A script that grows an action or a flag needs its row in that
script's tables, too.

---

## 2. Make targets

<!-- GEN:make-targets -->
**The terminal solver: install / uninstall (local)**

| target | what it does |
| --- | --- |
| `make install-all` | Full developer install: system deps → venv → all dependency groups → git hooks → completions |
| `make install-minimal` | Minimal install: base + solutions + show (no dev tools) |
| `make install-system` | Install system packages (apt) via setup script |
| `make install-chrome` | Install Chrome browser |
| `make install-primesieve-numpy` | Build & install the optional primesieve.numpy extension from source (NumPy 2.x) |
| `make install-completions` | Install bash tab-completions for all project scripts |
| `make uninstall-completions` | Remove bash tab-completions |
| `make install-hooks` | Install git hooks into .git/hooks/ and reset hooksPath to default |
| `make uninstall-hooks` | Remove git hooks from .git/hooks/ |
| `make install-credentials` | Configure gh as the git credential helper (logging in first if needed) and set the git identity |
| `make install-claude` | Install the Claude Code CLI (driven by the AI commands claude-solve / claude-blog) |
| `make uninstall-claude` | Remove the Claude Code CLI |
| `make install-nodejs` | Install a standalone Node.js under ~/.local (dev-only, no sudo; drives the SRP interop test) |
| `make uninstall-nodejs` | Remove the standalone Node.js installed by install-nodejs |
| `make uninstall` | Remove the venv (system deps must be removed separately) |

**Day to day: tests, the shell, versions, the audit**

| target | what it does |
| --- | --- |
| `make test` | Run the unit test suite (tests/) |
| `make run` | Run the interactive solver shell |
| `make version` | Show the running build's version (packages/solver/solver/version.py, plus how far HEAD is past its tag) |
| `make release` | Cut a release: bump packages/solver/solver/version.py from Conventional Commits, commit, tag, and push the commit + tag to origin. ARGS=--dry-run previews; ARGS=--no-push stops before publishing. |
| `make check-version` | Guard: the version redeploy-web would ship (packages/solver/solver/version.py) must have its vX.Y.Z tag on origin, so a redeploy never runs a release collaborator clones cannot reach (a locally-tagged-but-unpushed release runs the venv ahead of every clone). Queries origin — needs network. A prerequisite of redeploy-web. |
| `make audit` | Audit what git stores across the WHOLE tracked tree (~25s): every file under solutions/private is encrypted at rest, and no file anywhere is a compiled binary. The git hooks only audit what you actually stage or push, so this is the periodic sweep that also covers blobs committed before the hooks were in place. Counts only; offenders are always listed. Per-file detail: scripts/git/audit.sh |

**The web stack: deploy / remove / redeploy (sudo + systemd)**

| target | what it does |
| --- | --- |
| `make deploy-system-venv` | Deploy the root-owned /opt/euler system venv the euler-* app services run from (sudo) |
| `make remove-system-venv` | Remove the /opt/euler system venv (leaves service identities, state, and units intact) (sudo) |
| `make redeploy-system-venv` | Rebuild the /opt/euler system venv from scratch: remove, then deploy (sudo) |
| `make deploy-frontend` | Deploy the web edge: Caddy + acme.sh + euler-caddy.service (see docs/web-server-guide.md) |
| `make remove-frontend` | Remove the web edge (prompts before deleting /etc/euler, acme.sh, and the service users) |
| `make upgrade-frontend` | Upgrade the web edge packages (Caddy + acme.sh; regenerate the Caddyfile + unit) |
| `make redeploy-frontend` | Refresh the static web-content + Caddyfile and reload the edge |
| `make deploy-egress` | Deploy the egress proxy: Squid domain-allowlist + euler-proxy.service (see docs/web-server-guide.md) |
| `make remove-egress` | Remove the egress proxy (prompts before deleting /etc/euler-proxy and the euler-proxy user) |
| `make upgrade-egress` | Upgrade the egress proxy package (Squid; regenerate the config + unit) |
| `make deploy-ddns` | Deploy the dynamic-DNS updater timer (public access only — keeps the A record current) |
| `make remove-ddns` | Remove the dynamic-DNS updater timer (name.com records left untouched) |
| `make deploy-firewall` | Deploy the kernel egress firewall: per-uid nftables ruleset + euler-firewall.service (DD-8) |
| `make remove-firewall` | Remove the kernel egress firewall (flushes the euler table; nothing else touched) |
| `make deploy-smtp` | Deploy the loopback SMTP relay: euler-smtp user + service, scoped Gmail creds (DD-8) |
| `make remove-smtp` | Remove the loopback SMTP relay (prompts before deleting smtp.env and the euler-smtp user) |
| `make upgrade-smtp` | Upgrade the loopback SMTP relay (alias of deploy: relay + config + unit, restart) |
| `make deploy-auth` | Deploy the auth-service runtime: euler-auth/euler-adm + /opt/euler venv + auth.env (DD-5/DD-6) |
| `make remove-auth` | Remove the auth service (prompts before deleting the venv, state, and identities) |
| `make upgrade-auth` | Upgrade the auth service (alias of deploy: pip re-install the repo into /opt/euler, refresh config + unit) |
| `make redeploy-auth` | Redeploy the shared /opt/euler venv (auth.sh owns it) + restart the auth service |
| `make deploy-msg` | Deploy the message spool: the euler-msg user + /etc/euler/msg.env + euler-msg.service (user<->staff threads; see docs/web-server-guide.md § Messaging). Needs the shared /opt/euler venv, which auth.sh owns — run deploy-auth first |
| `make remove-msg` | Remove the message spool (prompts before deleting the threads and the identity) |
| `make upgrade-msg` | Upgrade the message spool (alias of deploy: refresh config + unit, restart) |
| `make redeploy-msg` | Restart the message spool against the current /opt/euler venv (redeploy-auth rebuilds that venv; this only bounces the service onto it) |
| `make deploy-site` | Deploy the public site: the euler-site user + /etc/euler/site.env + euler-site.service, serving the packaged content (euler-content, installed into the shared venv by deploy-auth) to signed-out visitors (docs/package-guide.md § 4) |
| `make remove-site` | Remove the public site (signed-out visitors get the login page again) |
| `make upgrade-site` | Upgrade the public site (alias of deploy: refresh config + unit, restart) |
| `make redeploy-site` | Restart the public site against the current /opt/euler venv and content package (redeploy-auth rebuilds both); deploys it when it is not installed yet |
| `make deploy-user` | Deploy the per-user provisioning layer (MT-7): the euler-user group, /etc/euler/user.env, and the euler-user@.service/.socket template. Per-collaborator uids/homes/clones are created later by `users add <email>` (euler_webshell.users → user.sh provision), which clones ~/euler straight from the public GitHub repo (ciphertext at rest, MT-13). |
| `make remove-user` | Remove the per-user layer (refuses while any provisioned collaborator remains) |
| `make upgrade-user` | Re-assert the shared per-user layer (alias of deploy; re-lays the unit template) |
| `make redeploy-user` | Fast path: refresh /etc/euler/user.env and bounce the running per-user instances (their sockets re-activate them against the freshly rebuilt venv; drops live shells) |
| `make deploy-web` | Deploy the full web stack, in dependency order: edge (Caddy+ACME+web-content), egress (Squid), DDNS, kernel egress firewall, SMTP relay, auth service (and the shared /opt/euler venv), message spool, public site, and the per-user provisioning layer. Each kit stays independently operable; the later kits reload the firewall as their service users appear. (sudo required) |
| `make remove-web` | Remove the full web stack (reverse order; the kits prompt before deleting state) |
| `make upgrade-web` | Upgrade the full web stack in place (regenerate configs, redeploy, restart; ddns and firewall have no upgrade action — their deploy is idempotent and doubles as one, and the firewall reload is the final consistency pass over the euler uids) |
| `make redeploy-web` | Fast redeploy of code, templates, and static assets WITHOUT touching identities, ACLs, units, certs, or the firewall: refresh the edge's static content + Caddyfile → rebuild the shared venv (auth) → restart the message spool and the public site on it → bounce the per-user instances so their sockets re-activate them against it. The edge goes first: the restarted services name each asset by a hash of its bytes (?v=, cached immutable), so those bytes must already be there. Note the running instances are stopped, so live terminals are dropped. The everyday "I changed Python/templates/CSS/JS, push it" turnaround. Gated on check-version so the deployed build's tag is on origin (run serially — the default — so the guard runs before any deploy step). |
| `make status-web` | Read-only, but needs sudo: the state it reads is root-owned (nftables, /etc/euler), the clones sit under 0700 homes, and the shell report is a query on each running instance's own socket. Each kit is run best-effort so one missing component (or a failing egress probe) never truncates the sweep. |
<!-- /GEN:make-targets -->

---

## 3. Scripts

<!-- GEN:script-table -->
**`scripts/`**

| script | what it does |
| --- | --- |
| [`bash_completions.sh`](../scripts/bash_completions.sh) | Bash completions for every project script: install, uninstall or render the completion file. |

**`scripts/c/`**

| script | what it does |
| --- | --- |
| [`compile.sh`](../scripts/c/compile.sh) | Compile a C solution into an executable, linked against the runner harness. |

**`scripts/content/`**

| script | what it does |
| --- | --- |
| [`stage.py`](../scripts/content/stage.py) | Stage the euler-content wheel source: `packages/content/` plus the public tree, in a scratch directory. |

**`scripts/docs/`**

| script | what it does |
| --- | --- |
| [`diagrams.py`](../scripts/docs/diagrams.py) | Capture the presentation's architecture diagrams as images for the guides and the README. |
| [`screenshots.py`](../scripts/docs/screenshots.py) | Capture the site's main pages for the README, as one animated GIF that cycles through them. |

**`scripts/fixes/`**

| script | what it does |
| --- | --- |
| [`fix_pycharm_dimmed_issue.sh`](../scripts/fixes/fix_pycharm_dimmed_issue.sh) | Fix PyCharm's translucent-overlay rendering on WSL2 by forcing X11. |

**`scripts/git/`**

| script | what it does |
| --- | --- |
| [`audit.sh`](../scripts/git/audit.sh) | Whole-tree audit of what git stores: private files encrypted, no compiled binaries. |
| [`configure-identity.sh`](../scripts/git/configure-identity.sh) | Configure gh as the git credential helper and set the git identity from the GitHub login. |
| [`publish.sh`](../scripts/git/publish.sh) | Publish directories to origin/master: pushed directly by the owner, otherwise as a pull request. |
| [`status.sh`](../scripts/git/status.sh) | Show how this clone stands against origin/master: divergence, committed and uncommitted changes. |
| [`sync.sh`](../scripts/git/sync.sh) | Bring the local repository in sync with origin/master. |

**`scripts/linters/`**

| script | what it does |
| --- | --- |
| [`check.sh`](../scripts/linters/check.sh) | Lint one directory: whitespace, mypy, flake8, shellcheck, plus docstrings and layering for packages. |
| [`layers.py`](../scripts/linters/layers.py) | The layering guard: dependencies between the three packages point one way. |

**`scripts/ops/`**

| script | what it does |
| --- | --- |
| [`release.sh`](../scripts/ops/release.sh) | Cut a new version and ship it — the whole release turnaround, in one command. |
| [`reset-user.sh`](../scripts/ops/reset-user.sh) | Reset one collaborator's clone to origin/master — the operator's repair of last resort. |

**`scripts/pip/`**

| script | what it does |
| --- | --- |
| [`upgrade.sh`](../scripts/pip/upgrade.sh) | Upgrade pip and the named packages in the active virtualenv. |

**`scripts/setup/`**

| script | what it does |
| --- | --- |
| [`auth.sh`](../scripts/setup/auth.sh) | Auth service kit (euler-auth): the sign-in service, and the shared /opt/euler venv it builds. |
| [`authoring_env.sh`](../scripts/setup/authoring_env.sh) | Shared reader for the authoring env (~/.euler/env) — which may be vault-encrypted |
| [`chrome.sh`](../scripts/setup/chrome.sh) | Install or remove Google Chrome, plus the /usr/local/bin/browser control script. |
| [`claude_code.sh`](../scripts/setup/claude_code.sh) | Install, update or remove the Claude Code CLI (`claude`) the AI commands drive. |
| [`ddns.sh`](../scripts/setup/ddns.sh) | Dynamic DNS kit (euler-ddns): keep the edge's A record on the host's public IP. |
| [`dev_env.sh`](../scripts/setup/dev_env.sh) | Install, uninstall or report the apt toolchains: C, Lua, Python and Ruby. |
| [`egress.sh`](../scripts/setup/egress.sh) | Egress proxy kit (euler-proxy): Squid with a domain allowlist, the only way out to the internet. |
| [`euler-ddns.sh`](../scripts/setup/euler-ddns.sh) | The euler DDNS runtime updater — deployed to /usr/local/bin/euler-ddns |
| [`euler-smtp.py`](../scripts/setup/euler-smtp.py) | euler-smtp — loopback SMTP submission relay (docs/web-server-guide.md § Egress). |
| [`firewall.sh`](../scripts/setup/firewall.sh) | Kernel egress firewall kit (nftables): per-uid rules for where each service may connect. |
| [`frontend.sh`](../scripts/setup/frontend.sh) | Web edge kit (euler-caddy): Caddy, acme.sh, the Caddyfile router and the static web content. |
| [`githooks.sh`](../scripts/setup/githooks.sh) | Render the git hooks from scripts/setup/hooks/ into .git/hooks/, or remove them. |
| [`msg.sh`](../scripts/setup/msg.sh) | Message spool kit (euler-msg): the user↔staff threads service. |
| [`nodejs.sh`](../scripts/setup/nodejs.sh) | Install or remove a standalone Node.js under ~/.local (dev tooling; no sudo, no apt). |
| [`primesieve_numpy_extension.sh`](../scripts/setup/primesieve_numpy_extension.sh) | Build and install the optional primesieve.numpy extension from source (NumPy 2.x). |
| [`pycharm_service.sh`](../scripts/setup/pycharm_service.sh) | Install the PyCharm wrapper script and its systemd user service. |
| [`site.sh`](../scripts/setup/site.sh) | Public site kit (euler-site): what signed-out visitors read, served from the euler-content wheel. |
| [`smtp.sh`](../scripts/setup/smtp.sh) | Loopback SMTP relay kit (euler-smtp): outbound mail, with its credentials scoped to the relay. |
| [`upgrade_service.sh`](../scripts/setup/upgrade_service.sh) | Install a systemd timer that runs an unattended apt upgrade every day. |
| [`user.sh`](../scripts/setup/user.sh) | Per-user tier kit (euler-user): the shared layer, and provisioning one collaborator at a time. |
| [`venv.sh`](../scripts/setup/venv.sh) | Shared system-venv helpers: the root-owned /opt/euler venv every euler-* service runs from. |

**`scripts/version/`**

| script | what it does |
| --- | --- |
| [`release.sh`](../scripts/version/release.sh) | Derive the next SemVer release from Conventional Commits, then bump, tag, and push it. |
<!-- /GEN:script-table -->
