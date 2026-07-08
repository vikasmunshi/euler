.PHONY: install-all install-minimal install-system install-chrome install-primesieve-numpy install-hooks uninstall-hooks install-completions uninstall-completions install-credentials install-claude uninstall-claude install-frontend uninstall-frontend upgrade-frontend install-egress uninstall-egress upgrade-egress install-ddns uninstall-ddns install-firewall uninstall-firewall install-smtp uninstall-smtp upgrade-smtp install-auth uninstall-auth upgrade-auth install-nodejs uninstall-nodejs install-web uninstall-web upgrade-web test run uninstall

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

## Full developer install: system deps → venv → all dependency groups → git hooks → completions
install-all: install-system install-chrome $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[ai,dev,show,solutions,web]"
	rm -rf solver.egg-info
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
	rm -rf solver.egg-info
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

## Install the web edge: Caddy + acme.sh + euler-caddy.service (see docs/server-redesign.md)
install-frontend:
	./scripts/setup/frontend.sh install
	@printf "✓ install-frontend complete: web edge installed (sudo systemctl for lifecycle)\n"

## Remove the web edge (prompts before deleting /etc/euler, acme.sh, and the service users)
uninstall-frontend:
	./scripts/setup/frontend.sh uninstall
	@printf "✓ uninstall-frontend complete: web edge removed\n"

## Upgrade the web edge (Caddy + acme.sh; regenerate the Caddyfile + unit)
upgrade-frontend:
	./scripts/setup/frontend.sh upgrade
	@printf "✓ upgrade-frontend complete: web edge upgraded\n"

## Install the egress proxy: Squid domain-allowlist + euler-proxy.service (see docs/server-redesign.md)
install-egress:
	./scripts/setup/egress.sh install
	@printf "✓ install-egress complete: egress proxy installed (sudo systemctl for lifecycle)\n"

## Remove the egress proxy (prompts before deleting /etc/euler-proxy and the euler-proxy user)
uninstall-egress:
	./scripts/setup/egress.sh uninstall
	@printf "✓ uninstall-egress complete: egress proxy removed\n"

## Upgrade the egress proxy (Squid; regenerate the config + unit)
upgrade-egress:
	./scripts/setup/egress.sh upgrade
	@printf "✓ upgrade-egress complete: egress proxy upgraded\n"

## Install the dynamic-DNS updater timer (public access only — keeps the A record current)
install-ddns:
	./scripts/setup/ddns.sh install
	@printf "✓ install-ddns complete: DDNS timer installed\n"

## Remove the dynamic-DNS updater timer (name.com records left untouched)
uninstall-ddns:
	./scripts/setup/ddns.sh uninstall
	@printf "✓ uninstall-ddns complete: DDNS timer removed\n"

## Install the kernel egress firewall: per-uid nftables ruleset + euler-firewall.service (DD-8)
install-firewall:
	./scripts/setup/firewall.sh install
	@printf "✓ install-firewall complete: euler egress ruleset loaded (boot-enabled)\n"

## Remove the kernel egress firewall (flushes the euler table; nothing else touched)
uninstall-firewall:
	./scripts/setup/firewall.sh uninstall
	@printf "✓ uninstall-firewall complete: euler egress ruleset removed\n"

## Install the loopback SMTP relay: euler-smtp user + service, scoped Gmail creds (DD-8)
install-smtp:
	./scripts/setup/smtp.sh install
	@printf "✓ install-smtp complete: loopback mail relay installed (sudo systemctl for lifecycle)\n"

## Remove the loopback SMTP relay (prompts before deleting smtp.env and the euler-smtp user)
uninstall-smtp:
	./scripts/setup/smtp.sh uninstall
	@printf "✓ uninstall-smtp complete: loopback mail relay removed\n"

## Upgrade the loopback SMTP relay (redeploy the relay + config + unit, restart)
upgrade-smtp:
	./scripts/setup/smtp.sh upgrade
	@printf "✓ upgrade-smtp complete: loopback mail relay upgraded\n"

## Install the auth-service runtime: euler-auth/euler-adm + /opt/euler venv + auth.env (DD-5/DD-6)
install-auth:
	./scripts/setup/auth.sh install
	@printf "✓ install-auth complete: auth runtime deployed (unit deferred until solver.web.auth lands)\n"

## Remove the auth service (prompts before deleting the venv, state, and identities)
uninstall-auth:
	./scripts/setup/auth.sh uninstall
	@printf "✓ uninstall-auth complete: auth service removed\n"

## Upgrade the auth service (pip re-install the repo into /opt/euler, refresh config + unit)
upgrade-auth:
	./scripts/setup/auth.sh upgrade
	@printf "✓ upgrade-auth complete: auth service upgraded\n"

## Install a standalone Node.js under ~/.local (dev-only; drives the SRP interop test)
install-nodejs:
	./scripts/setup/nodejs.sh install
	@printf "✓ install-nodejs complete\n"

## Remove the standalone Node.js installed by install-nodejs
uninstall-nodejs:
	./scripts/setup/nodejs.sh uninstall
	@printf "✓ uninstall-nodejs complete\n"

## Install the full web stack, in dependency order: edge (Caddy+ACME+web-content),
## egress (Squid), DDNS, kernel egress firewall, SMTP relay, auth service.
## Each kit stays independently operable; the later kits reload the firewall as
## their service users appear. (sudo required; see docs/server-redesign.md)
install-web: install-frontend install-egress install-ddns install-firewall install-smtp install-auth
	@printf "✓ install-web complete: full web stack installed\n"

## Remove the full web stack (reverse order; the kits prompt before deleting state)
uninstall-web: uninstall-auth uninstall-smtp uninstall-firewall uninstall-ddns uninstall-egress uninstall-frontend
	@printf "✓ uninstall-web complete: full web stack removed\n"

## Upgrade the full web stack in place (regenerate configs, redeploy, restart;
## ddns.sh install is its idempotent upgrade, and the firewall reload is the
## final consistency pass over the euler uids)
upgrade-web: upgrade-frontend upgrade-egress install-ddns upgrade-smtp upgrade-auth
	./scripts/setup/firewall.sh reload
	@printf "✓ upgrade-web complete: full web stack upgraded\n"

# Standalone Node.js (no sudo):

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
