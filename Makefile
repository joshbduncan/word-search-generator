VENV:=.venv
BIN:=$(VENV)/bin

.DEFAULT_GOAL := help
.PHONY: help dev ipython clean cleanup lint typing test format nox build release
##@ General
help: ## Display this help section
	@echo $(MAKEFILE_LIST)
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
dev: ## build a virtual environment for development
	@echo "🏗️ setting up development environment..."
	uv sync --all-extras

ipython: ## run ipython inside of the uv venv
	uv run --with ipython ipython

clean: ## clean build artifacts and cache files
	@echo "🧹 cleaning..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

cleanup: format lint typing ## format, lint, and type check

lint: ## lint the app using ruff
	@echo "📝 linting..."
	uv run ruff check --fix

typing: ## type check the app using ty
	@echo "📝 type checking..."
	uv run ty check src tests

test: ## test the app using pytest
	@echo "🧪 running test suite..."
	uv run pytest -vv --cov=src --cov-report term-missing

format: ## runs cleaners
	@echo "🧾 formatting..."
	uv run ruff format

nox: ## runs linting, formatting, type checking, and tests on all specified envs via nox
	@echo "🎯 nox..."
	uv run nox

##@ Build
build: cleanup test ## build the app package
	@echo "🏗️ building package..."
	uv build

##@ Release
release: build ## release on pypi (with verification)
	@echo "🚀 uploading to PyPI..."
	uv publish
