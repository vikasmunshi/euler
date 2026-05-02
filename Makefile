.PHONY: install install-dev install-system install-python run clean

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

## Full developer install: system deps → venv → all dependency groups → pre-commit hooks
install: install-system install-chrome install-solver install-pre-commit

## Install the solver as a local package
install-solver: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[show,solutions,dev]"
	rm -rf solver.egg-info

## Minimal install: base + solutions + show (no dev tools)
install-user: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[show,solutions]"
	rm -rf solver.egg-info

## Install system packages (apt) via setup script
install-system:
	./scripts/setup_dev_env.sh install python primesieve c

## Install Chrome browser
install-chrome:
	./scripts/setup_chrome.sh install

# Install pre-commit
install-pre-commit: $(VENV)
	$(VENV)/bin/pre-commit install


## Create venv if it doesn't exist
$(VENV):
	python3.14 -m venv $(VENV)

## Run the interactive solver shell
run: $(VENV)
	$(VENV)/bin/solver

## Remove the venv (system deps must be removed separately)
clean:
	rm -rf $(VENV) solver.egg-info
	@printf "To remove system dependencies run:\n\t./scripts/setup_dev_env.sh uninstall python primesieve c\n"
