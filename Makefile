# Target verbs, by kind:
#   local  (terminal solver, incl. system packages) — install / uninstall
#   system (the web stack, sudo + systemd)         — deploy / remove / redeploy [/ upgrade]
# Each system target's verb matches the action its script in scripts/setup/ takes.

.PHONY: install-all install-minimal install-system install-chrome install-primesieve-numpy \
        install-hooks uninstall-hooks install-completions uninstall-completions \
        install-credentials install-claude uninstall-claude install-nodejs uninstall-nodejs \
        deploy-system-venv remove-system-venv redeploy-system-venv \
        deploy-frontend remove-frontend upgrade-frontend redeploy-frontend \
        deploy-egress remove-egress upgrade-egress \
        deploy-ddns remove-ddns \
        deploy-firewall remove-firewall \
        deploy-smtp remove-smtp upgrade-smtp \
        deploy-auth remove-auth upgrade-auth redeploy-auth \
        deploy-user remove-user upgrade-user redeploy-user \
        deploy-web remove-web upgrade-web redeploy-web \
        test run uninstall

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

## Full developer install: system deps → venv → all dependency groups → git hooks → completions
install-all: install-system install-chrome $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[ai,dev,show,solutions,web]"
	rm -rf build solver.egg-info
	$(MAKE) install-primesieve-numpy
	$(MAKE) install-hooks
	$(MAKE) install-completions
	$(MAKE) install-credentials
	$(MAKE) install-claude
	@printf "✓ install-all complete: full developer environment ready\n"

## Minimal install: base + solutions + show (no dev tools)
install-minimal: install-system install-chrome $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[show,solutions,web]"
	rm -rf build solver.egg-info
	$(MAKE) install-primesieve-numpy
	@printf "✓ install-minimal complete: base environment ready\n"

## Install system packages (apt) via setup script
install-system:
	./scripts/setup/dev_env.sh install python primesieve c
	@printf "✓ install-system complete: apt packages installed\n"

## Install Chrome browser
install-chrome:
	./scripts/setup/chrome.sh install
	@printf "✓ install-chrome complete: Chrome installed\n"

## Build & install the optional primesieve.numpy extension from source (NumPy 2.x)
install-primesieve-numpy: $(VENV)
	./scripts/setup/primesieve_numpy_extension.sh install
	@printf "✓ install-primesieve-numpy complete: primesieve.numpy extension ready\n"

## Install bash tab-completions for all project scripts
install-completions:
	./scripts/bash_completions.sh install
	@printf "✓ install-completions complete: bash completions installed\n"

## Remove bash tab-completions
uninstall-completions:
	./scripts/bash_completions.sh uninstall
	@printf "✓ uninstall-completions complete: bash completions removed\n"

## Install git hooks into .git/hooks/ and reset hooksPath to default
install-hooks:
	git config --unset core.hooksPath || true
	./scripts/setup/githooks.sh install --force
	@printf "✓ install-hooks complete: git hooks installed\n"

## Remove git hooks from .git/hooks/
uninstall-hooks:
	./scripts/setup/githooks.sh uninstall
	@printf "✓ uninstall-hooks complete: git hooks removed\n"

## Configure gh as the git credential helper (logging in first if needed) and set the git identity
install-credentials:
	./scripts/git/configure-identity.sh
	@printf "✓ install-credentials complete: gh configured as git credential helper, git identity set\n"

## Install the Claude Code CLI (used by the AI features: claude-solver / make)
install-claude:
	./scripts/setup/claude_code.sh install
	@printf "✓ install-claude complete: Claude Code CLI installed\n"

## Remove the Claude Code CLI
uninstall-claude:
	./scripts/setup/claude_code.sh uninstall
	@printf "✓ uninstall-claude complete: Claude Code CLI removed\n"

## Install a standalone Node.js under ~/.local (dev-only, no sudo; drives the SRP interop test)
install-nodejs:
	./scripts/setup/nodejs.sh install
	@printf "✓ install-nodejs complete\n"

## Remove the standalone Node.js installed by install-nodejs
uninstall-nodejs:
	./scripts/setup/nodejs.sh uninstall
	@printf "✓ uninstall-nodejs complete\n"

## Create venv if it doesn't exist
$(VENV):
	python3.14 -m venv $(VENV)
	@printf "✓ venv created at $(VENV)\n"

## Run the unit test suite (tests/)
test: $(VENV)
	$(PYTHON) -m unittest discover -s tests -t .

## Run the interactive solver shell
run: $(VENV)
	$(VENV)/bin/solver

## Remove the venv (system deps must be removed separately)
uninstall: uninstall-hooks uninstall-completions
	rm -rf $(VENV) solver.egg-info
	@printf "✓ uninstall complete: venv removed\n"
	@printf "To remove system dependencies run:\n\t./scripts/setup/dev_env.sh uninstall python primesieve c\n"
	@printf "To remove the Claude Code CLI run:\n\tmake uninstall-claude\n"

# ── The web stack: deploy / remove / redeploy (sudo + systemd) ─────────────────────

## Deploy the root-owned /opt/euler system venv the euler-* app services run from (sudo)
deploy-system-venv:
	./scripts/setup/venv.sh deploy
	@printf "✓ deploy-system-venv complete: /opt/euler venv deployed\n"

## Remove the /opt/euler system venv (leaves service identities, state, and units intact) (sudo)
remove-system-venv:
	./scripts/setup/venv.sh remove
	@printf "✓ remove-system-venv complete: /opt/euler venv removed\n"

## Rebuild the /opt/euler system venv from scratch: remove, then deploy (sudo)
redeploy-system-venv:
	./scripts/setup/venv.sh redeploy
	@printf "✓ redeploy-system-venv complete: /opt/euler venv rebuilt\n"

## Deploy the web edge: Caddy + acme.sh + euler-caddy.service (see docs/web-server-guide.md)
deploy-frontend:
	./scripts/setup/frontend.sh deploy
	@printf "✓ deploy-frontend complete: web edge deployed (sudo systemctl for lifecycle)\n"

## Remove the web edge (prompts before deleting /etc/euler, acme.sh, and the service users)
remove-frontend:
	./scripts/setup/frontend.sh remove
	@printf "✓ remove-frontend complete: web edge removed\n"

## Upgrade the web edge packages (Caddy + acme.sh; regenerate the Caddyfile + unit)
upgrade-frontend:
	./scripts/setup/frontend.sh upgrade
	@printf "✓ upgrade-frontend complete: web edge upgraded\n"

## Refresh the static web-content + Caddyfile and reload the edge
redeploy-frontend:
	./scripts/setup/frontend.sh redeploy
	@printf "✓ redeploy-frontend complete: web-content + Caddyfile reloaded\n"

## Deploy the egress proxy: Squid domain-allowlist + euler-proxy.service (see docs/web-server-guide.md)
deploy-egress:
	./scripts/setup/egress.sh deploy
	@printf "✓ deploy-egress complete: egress proxy deployed (sudo systemctl for lifecycle)\n"

## Remove the egress proxy (prompts before deleting /etc/euler-proxy and the euler-proxy user)
remove-egress:
	./scripts/setup/egress.sh remove
	@printf "✓ remove-egress complete: egress proxy removed\n"

## Upgrade the egress proxy package (Squid; regenerate the config + unit)
upgrade-egress:
	./scripts/setup/egress.sh upgrade
	@printf "✓ upgrade-egress complete: egress proxy upgraded\n"

## Deploy the dynamic-DNS updater timer (public access only — keeps the A record current)
deploy-ddns:
	./scripts/setup/ddns.sh deploy
	@printf "✓ deploy-ddns complete: DDNS timer deployed\n"

## Remove the dynamic-DNS updater timer (name.com records left untouched)
remove-ddns:
	./scripts/setup/ddns.sh remove
	@printf "✓ remove-ddns complete: DDNS timer removed\n"

## Deploy the kernel egress firewall: per-uid nftables ruleset + euler-firewall.service (DD-8)
deploy-firewall:
	./scripts/setup/firewall.sh deploy
	@printf "✓ deploy-firewall complete: euler egress ruleset loaded (boot-enabled)\n"

## Remove the kernel egress firewall (flushes the euler table; nothing else touched)
remove-firewall:
	./scripts/setup/firewall.sh remove
	@printf "✓ remove-firewall complete: euler egress ruleset removed\n"

## Deploy the loopback SMTP relay: euler-smtp user + service, scoped Gmail creds (DD-8)
deploy-smtp:
	./scripts/setup/smtp.sh deploy
	@printf "✓ deploy-smtp complete: loopback mail relay deployed (sudo systemctl for lifecycle)\n"

## Remove the loopback SMTP relay (prompts before deleting smtp.env and the euler-smtp user)
remove-smtp:
	./scripts/setup/smtp.sh remove
	@printf "✓ remove-smtp complete: loopback mail relay removed\n"

## Upgrade the loopback SMTP relay (alias of deploy: relay + config + unit, restart)
upgrade-smtp:
	./scripts/setup/smtp.sh upgrade
	@printf "✓ upgrade-smtp complete: loopback mail relay upgraded\n"

## Deploy the auth-service runtime: euler-auth/euler-adm + /opt/euler venv + auth.env (DD-5/DD-6)
deploy-auth:
	./scripts/setup/auth.sh deploy
	@printf "✓ deploy-auth complete: auth runtime deployed\n"

## Remove the auth service (prompts before deleting the venv, state, and identities)
remove-auth:
	./scripts/setup/auth.sh remove
	@printf "✓ remove-auth complete: auth service removed\n"

## Upgrade the auth service (alias of deploy: pip re-install the repo into /opt/euler,
## refresh config + unit)
upgrade-auth:
	./scripts/setup/auth.sh upgrade
	@printf "✓ upgrade-auth complete: auth service upgraded\n"

## Redeploy the shared /opt/euler venv (auth.sh owns it) + restart the auth service
redeploy-auth:
	./scripts/setup/auth.sh redeploy
	@printf "✓ redeploy-auth complete: venv + authorizations refreshed, auth restarted\n"

## Deploy the per-user provisioning layer (MT-7): the euler-user group,
## /etc/euler/user.env, and the euler-user@.service/.socket template. Per-collaborator
## uids/homes/clones are created later by `users add <email>`
## (solver.web.auth.commands → user.sh provision), which clones ~/euler straight
## from the public GitHub repo (ciphertext at rest, MT-13).
deploy-user:
	./scripts/setup/user.sh deploy
	@printf "✓ deploy-user complete: per-user provisioning layer deployed\n"

## Remove the per-user layer (refuses while any euler-user-<slug> remains)
remove-user:
	./scripts/setup/user.sh remove
	@printf "✓ remove-user complete: per-user provisioning layer removed\n"

## Re-assert the shared per-user layer (alias of deploy; re-lays the unit template)
upgrade-user:
	./scripts/setup/user.sh upgrade
	@printf "✓ upgrade-user complete: per-user provisioning layer upgraded\n"

## Fast path: refresh /etc/euler/user.env and bounce the running per-user instances
## (their sockets re-activate them against the freshly rebuilt venv; drops live shells)
redeploy-user:
	./scripts/setup/user.sh redeploy
	@printf "✓ redeploy-user complete: per-user config refreshed, instances bounced\n"

## Deploy the full web stack, in dependency order: edge (Caddy+ACME+web-content),
## egress (Squid), DDNS, kernel egress firewall, SMTP relay, auth service, and the
## per-user provisioning layer (MT-4 — the retired per-profile content/ws kits are
## no longer deployed). Each kit stays independently operable; the later kits
## reload the firewall as their service users appear. (sudo required)
deploy-web: deploy-frontend deploy-egress deploy-ddns deploy-firewall deploy-smtp deploy-auth deploy-user
	@printf "✓ deploy-web complete: full web stack deployed\n"

## Remove the full web stack (reverse order; the kits prompt before deleting state)
remove-web: remove-user remove-auth remove-smtp remove-firewall remove-ddns remove-egress remove-frontend
	@printf "✓ remove-web complete: full web stack removed\n"

## Upgrade the full web stack in place (regenerate configs, redeploy, restart;
## ddns and firewall have no upgrade action — their deploy is idempotent and doubles
## as one, and the firewall reload is the final consistency pass over the euler uids)
upgrade-web: upgrade-frontend upgrade-egress deploy-ddns upgrade-smtp upgrade-auth upgrade-user
	./scripts/setup/firewall.sh reload
	@printf "✓ upgrade-web complete: full web stack upgraded\n"

## Fast redeploy of code, templates, and static assets WITHOUT touching identities,
## ACLs, units, certs, or the firewall: rebuild the shared venv (auth) → bounce the
## per-user instances so their sockets re-activate them against it → refresh the
## edge's static content + Caddyfile. Note the running instances are stopped, so
## live terminals are dropped. The everyday "I changed Python/templates/CSS/JS,
## push it" turnaround.
redeploy-web: redeploy-auth redeploy-user redeploy-frontend
	@printf "✓ redeploy-web complete: code, templates, and static assets redeployed\n"
