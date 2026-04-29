.PHONY: install install-system install-python run clean

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

## Full install: system deps → venv → python deps → pre-commit hooks
install: system-install $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e .
	rm -rf solver.egg-info
	$(VENV)/bin/pre-commit install

## Install system packages (apt) via setup script
system-install:
	./scripts/setup_dev_env.sh install python primesieve c

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
