# AlgoTree Makefile

# Variables
PYTHON := python3
PIP := pip
PACKAGE_NAME := AlgoTree
VERSION_FILE := setup.py
CURRENT_VERSION := $(shell grep -oP "version=\"\K[^\"]*" $(VERSION_FILE))
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

# Use virtual environment if it exists
ifneq ($(wildcard $(VENV)/bin/activate),)
    PYTHON := $(VENV_PYTHON)
    PIP := $(VENV_PIP)
endif

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Find source files
SOURCES := $(shell find $(PACKAGE_NAME) -name "*.py")
TESTS := $(shell find test -name "*.py")

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help install install-dev test test-verbose lint format clean clean-all docs coverage build release-pypi
.PHONY: version-patch version-minor version-major tag push-tag release-check release release-minor release-major
.PHONY: venv venv-clean venv-activate dev check all setup
.PHONY: docs-serve docs-open docs-deploy-gh-pages docs-clean

## Help
help:
	@echo "$(BLUE)AlgoTree Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Environment:$(NC)"
	@echo "  make venv          Create virtual environment"
	@echo "  make venv-clean    Remove virtual environment"
	@echo "  make venv-activate Show activation command"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make install        Install runtime dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo "  make test          Run unit tests"
	@echo "  make test-verbose  Run tests with verbose output"
	@echo "  make lint          Run code linting"
	@echo "  make format        Format code with black (if installed)"
	@echo "  make coverage      Run tests with coverage report"
	@echo "  make clean         Clean build artifacts"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make docs          Generate documentation"
	@echo "  make docs-serve    Serve docs locally on port 8000"
	@echo "  make docs-open     Open docs in browser"
	@echo "  make docs-deploy-gh-pages  Deploy to GitHub Pages"
	@echo "  make docs-clean    Clean documentation build"
	@echo ""
	@echo "$(GREEN)Release Management:$(NC)"
	@echo "  make version-patch  Bump patch version (0.0.X)"
	@echo "  make version-minor  Bump minor version (0.X.0)"
	@echo "  make version-major  Bump major version (X.0.0)"
	@echo "  make release       Full release: test, bump patch, tag, and upload to PyPI"
	@echo "  make release-minor  Full release with minor version bump"
	@echo "  make release-major  Full release with major version bump"
	@echo ""
	@echo "$(YELLOW)Current version: $(CURRENT_VERSION)$(NC)"
	@if [ -d "$(VENV)" ]; then \
		echo "$(GREEN)Virtual environment: Active ($(VENV))$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment: Not created (run 'make venv')$(NC)"; \
	fi

## Virtual Environment Management
venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
		$(VENV_PIP) install --upgrade pip setuptools wheel; \
		echo "$(GREEN)Virtual environment created at $(VENV)$(NC)"; \
		echo "$(YELLOW)Run 'source $(VENV)/bin/activate' or 'make venv-activate' to activate$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment already exists at $(VENV)$(NC)"; \
	fi

venv-clean:
	@echo "$(BLUE)Removing virtual environment...$(NC)"
	@if [ -d "$(VENV)" ]; then \
		rm -rf $(VENV); \
		echo "$(GREEN)Virtual environment removed$(NC)"; \
	else \
		echo "$(YELLOW)No virtual environment found$(NC)"; \
	fi

venv-activate:
	@echo "$(BLUE)To activate the virtual environment, run:$(NC)"
	@echo "$(GREEN)source $(VENV)/bin/activate$(NC)"

## Installation
install: venv
	@echo "$(BLUE)Installing runtime dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo "$(GREEN)Dependencies installed$(NC)"

install-dev: venv install
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install black flake8 pytest pytest-cov wheel twine
	@echo "$(GREEN)Development dependencies installed$(NC)"

## Testing
test:
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m unittest discover -s test

test-verbose:
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	$(PYTHON) -m unittest discover -s test -v

## Code Quality
lint:
	@echo "$(BLUE)Running linter...$(NC)"
	$(PYTHON) -m flake8 $(SOURCES) $(TESTS)

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black $(SOURCES) $(TESTS); \
	else \
		echo "$(RED)black not installed. Run 'make install-dev' first.$(NC)"; \
	fi

## Documentation
docs: install
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Ensuring package is installed in editable mode...$(NC)"
	$(PIP) install -e . --quiet
	sphinx-apidoc -f -o source $(PACKAGE_NAME)
	cd source && sphinx-build -b html . ../docs
	@echo "$(GREEN)Documentation generated in docs/$(NC)"

docs-serve: docs
	@echo "$(BLUE)Starting documentation server...$(NC)"
	@echo "$(GREEN)Documentation available at http://localhost:8000$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop the server$(NC)"
	cd docs && python -m http.server 8000

docs-open: docs
	@echo "$(BLUE)Opening documentation in browser...$(NC)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open docs/index.html; \
	elif command -v open >/dev/null 2>&1; then \
		open docs/index.html; \
	else \
		echo "$(YELLOW)Please open docs/index.html in your browser$(NC)"; \
	fi

docs-deploy-gh-pages: docs
	@echo "$(BLUE)Deploying documentation to GitHub Pages...$(NC)"
	@if [ ! -d ".git" ]; then \
		echo "$(RED)Error: Not a git repository$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Checking out gh-pages branch...$(NC)"
	@if git show-ref --quiet refs/heads/gh-pages; then \
		git checkout gh-pages; \
		git pull origin gh-pages; \
	else \
		git checkout --orphan gh-pages; \
		git rm -rf .; \
		git clean -fdx; \
	fi
	@echo "$(YELLOW)Copying documentation...$(NC)"
	cp -r docs/* .
	echo "queelius.github.io/AlgoTree" > CNAME || true
	git add -A
	git commit -m "Update documentation" || true
	git push origin gh-pages
	git checkout -
	@echo "$(GREEN)Documentation deployed to GitHub Pages$(NC)"
	@echo "$(GREEN)Visit: https://queelius.github.io/AlgoTree/$(NC)"

docs-clean:
	@echo "$(BLUE)Cleaning documentation...$(NC)"
	rm -rf docs/_build docs/_static docs/_templates
	rm -f source/$(PACKAGE_NAME).rst source/modules.rst
	@echo "$(GREEN)Documentation cleaned$(NC)"

## Coverage
coverage:
	@echo "$(BLUE)Running coverage analysis...$(NC)"
	coverage run -m unittest discover -s test
	coverage report
	coverage html
	coverage json
	@echo "$(GREEN)Coverage report generated$(NC)"

## Build
build: clean
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)Build complete$(NC)"

## Cleaning
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .coverage htmlcov coverage.json
	@echo "$(GREEN)Clean complete$(NC)"

clean-all: clean venv-clean
	@echo "$(GREEN)Full clean complete (including virtual environment)$(NC)"

## Version Management
version-patch:
	@echo "$(BLUE)Bumping patch version...$(NC)"
	@NEW_VERSION=$$(echo $(CURRENT_VERSION) | awk -F. '{$$NF = $$NF + 1;} 1' | sed 's/ /./g'); \
	sed -i "s/version=\"$(CURRENT_VERSION)\"/version=\"$$NEW_VERSION\"/" $(VERSION_FILE); \
	echo "$(GREEN)Version bumped from $(CURRENT_VERSION) to $$NEW_VERSION$(NC)"

version-minor:
	@echo "$(BLUE)Bumping minor version...$(NC)"
	@NEW_VERSION=$$(echo $(CURRENT_VERSION) | awk -F. '{$$2 = $$2 + 1; $$3 = 0;} 1' | sed 's/ /./g'); \
	sed -i "s/version=\"$(CURRENT_VERSION)\"/version=\"$$NEW_VERSION\"/" $(VERSION_FILE); \
	echo "$(GREEN)Version bumped from $(CURRENT_VERSION) to $$NEW_VERSION$(NC)"

version-major:
	@echo "$(BLUE)Bumping major version...$(NC)"
	@NEW_VERSION=$$(echo $(CURRENT_VERSION) | awk -F. '{$$1 = $$1 + 1; $$2 = 0; $$3 = 0;} 1' | sed 's/ /./g'); \
	sed -i "s/version=\"$(CURRENT_VERSION)\"/version=\"$$NEW_VERSION\"/" $(VERSION_FILE); \
	echo "$(GREEN)Version bumped from $(CURRENT_VERSION) to $$NEW_VERSION$(NC)"

## Git/GitHub Management
tag:
	@echo "$(BLUE)Creating git tag...$(NC)"
	@NEW_VERSION=$$(grep -oP "version=\"\K[^\"]*" $(VERSION_FILE)); \
	git add $(VERSION_FILE); \
	git commit -m "Bump version to $$NEW_VERSION" || true; \
	git tag -a "v$$NEW_VERSION" -m "Release version $$NEW_VERSION"; \
	echo "$(GREEN)Tagged version $$NEW_VERSION$(NC)"

push-tag:
	@echo "$(BLUE)Pushing to GitHub...$(NC)"
	git push origin main
	git push origin --tags
	@echo "$(GREEN)Pushed to GitHub$(NC)"

## PyPI Release
release-pypi: build
	@echo "$(BLUE)Uploading to PyPI...$(NC)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)Released to PyPI$(NC)"

## Release Checks
release-check:
	@echo "$(BLUE)Running release checks...$(NC)"
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "$(RED)Error: Working directory is not clean. Commit or stash changes.$(NC)"; \
		exit 1; \
	fi
	@if ! git diff-index --quiet HEAD --; then \
		echo "$(RED)Error: There are uncommitted changes.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Release checks passed$(NC)"

## Full Release Process
release: release-check test lint version-patch tag push-tag release-pypi clean
	@echo "$(GREEN)Release complete!$(NC)"

release-minor: release-check test lint version-minor tag push-tag release-pypi clean
	@echo "$(GREEN)Minor release complete!$(NC)"

release-major: release-check test lint version-major tag push-tag release-pypi clean
	@echo "$(GREEN)Major release complete!$(NC)"

## Development Shortcuts
dev: venv install-dev
	@echo "$(GREEN)Development environment ready$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV)/bin/activate$(NC)"

check: test lint
	@echo "$(GREEN)All checks passed$(NC)"

all: clean install test lint docs build
	@echo "$(GREEN)Full build complete$(NC)"

# Quick setup for new developers
setup: venv install-dev
	@echo "$(GREEN)Project setup complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Activate virtual environment: source $(VENV)/bin/activate"
	@echo "  2. Run tests: make test"
	@echo "  3. Start developing!"