VENV:=.venv
BIN:=$(VENV)/bin
PWD := $(realpath $(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

.DEFAULT_GOAL := help
.PHONY: help
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

polish: cleanup test  ## cleans and lints before running the test suite

verify: test ## run all verification steps
	@echo "✅ all checks passed"

nox: ## runs linting, formatting, type checking, and tests on all specified envs via nox
	@echo "🎯 nox..."
	uv run nox -p

##@ Build
build: cleanup ## build the app package
	@echo "🏗️ building package..."
	uv build

##@ Release
pre-release: build ## verify package before release
	@echo "🔍 verifying package..."
	uvx twine check dist/*
	@echo "📋 package contents:"
	@ls -la dist/

release: pre-release ## release on pypi (with verification)
	@echo "🚀 uploading to PyPI..."
	uvx twine upload dist/*.whl dist/*.tar.gz
