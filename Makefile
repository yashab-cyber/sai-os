.PHONY: install install-dev install-voice install-desktop setup-ollama test lint clean iso help

PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := .venv
VENV_BIN := $(VENV)/bin

help: ## Show this help message
	@echo "SAI-OS Build System"
	@echo "==================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip setuptools wheel

install: venv ## Install SAI-OS core
	$(VENV_BIN)/pip install -e ".[dev]"

install-voice: install ## Install with voice support
	$(VENV_BIN)/pip install -e ".[voice]"

install-desktop: install ## Install with desktop shell
	$(VENV_BIN)/pip install -e ".[desktop]"

install-all: venv ## Install everything
	$(VENV_BIN)/pip install -e ".[dev,voice,desktop]"

setup-ollama: ## Install Ollama and download default model
	bash scripts/setup-ollama.sh

test: ## Run test suite
	$(VENV_BIN)/python -m pytest tests/ -v --tb=short

lint: ## Run linters
	$(VENV_BIN)/python -m ruff check sai_core/ sai_desktop/
	$(VENV_BIN)/python -m mypy sai_core/

format: ## Auto-format code
	$(VENV_BIN)/python -m ruff format sai_core/ sai_desktop/

clean: ## Clean build artifacts
	rm -rf build/live-image-*.iso
	rm -rf dist/ *.egg-info
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -name "*.pyc" -delete

iso: ## Build bootable ISO (requires root + live-build)
	cd build && sudo lb clean && sudo lb config && sudo lb build
	@echo "\n✅ ISO built: build/live-image-amd64.hybrid.iso"

run-shell: ## Launch SAI Shell
	$(VENV_BIN)/sai

run-daemon: ## Launch SAI Daemon
	$(VENV_BIN)/sai-daemon

run-desktop: ## Launch SAI Desktop Shell
	$(VENV_BIN)/sai-desktop
