.PHONY: install-all install-minimal install-system install-chrome install-primesieve-numpy install-hooks uninstall-hooks install-completions uninstall-completions install-credentials install-claude uninstall-claude run uninstall

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

## Configure gh as the git credential helper (logging in first if needed)
install-credentials:
	gh auth status >/dev/null 2>&1 || gh auth login
	gh auth setup-git
	@printf "✓ install-credentials complete: gh configured as git credential helper\n"

## Install the Claude Code CLI (used by the AI features: claude-solver / make)
install-claude:
	./scripts/setup/claude_code.sh install
	@printf "✓ install-claude complete: Claude Code CLI installed\n"

## Remove the Claude Code CLI
uninstall-claude:
	./scripts/setup/claude_code.sh uninstall
	@printf "✓ uninstall-claude complete: Claude Code CLI removed\n"

## Create venv if it doesn't exist
$(VENV):
	python3.14 -m venv $(VENV)
	@printf "✓ venv created at $(VENV)\n"

## Run the interactive solver shell
run: $(VENV)
	$(VENV)/bin/solver

## Remove the venv (system deps must be removed separately)
uninstall: uninstall-hooks uninstall-completions
	rm -rf $(VENV) solver.egg-info
	@printf "✓ uninstall complete: venv removed\n"
	@printf "To remove system dependencies run:\n\t./scripts/setup/dev_env.sh uninstall python primesieve c\n"
	@printf "To remove the Claude Code CLI run:\n\tmake uninstall-claude\n"
