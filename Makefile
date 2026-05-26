.PHONY: install-all install-minimal install-system install-chrome install-hooks uninstall-hooks install-completions uninstall-completions run uninstall

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

## Full developer install: system deps → venv → all dependency groups → git hooks → completions
install-all: install-system install-chrome $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[ai,dev,show,solutions]"
	rm -rf solver.egg-info
	$(MAKE) install-hooks
	$(MAKE) install-completions

## Minimal install: base + solutions + show (no dev tools)
install-minimal: install-system install-chrome $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[show,solutions]"
	rm -rf solver.egg-info

## Install system packages (apt) via setup script
install-system:
	./scripts/setup/dev_env.sh install python primesieve c

## Install Chrome browser
install-chrome:
	./scripts/setup/chrome.sh install

## Install bash tab-completions for all project scripts
install-completions:
	./scripts/bash_completions.sh install

## Remove bash tab-completions
uninstall-completions:
	./scripts/bash_completions.sh uninstall

## Install git hooks into .git/hooks/ and reset hooksPath to default
install-hooks:
	git config --unset core.hooksPath || true
	./scripts/setup/githooks.sh install --force

## Remove git hooks from .git/hooks/
uninstall-hooks:
	./scripts/setup/githooks.sh uninstall

## Create venv if it doesn't exist
$(VENV):
	python3.14 -m venv $(VENV)

## Run the interactive solver shell
run: $(VENV)
	$(VENV)/bin/solver

## Remove the venv (system deps must be removed separately)
uninstall: uninstall-hooks uninstall-completions
	rm -rf $(VENV) solver.egg-info
	@printf "To remove system dependencies run:\n\t./scripts/setup/dev_env.sh uninstall python primesieve c\n"
