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
	uv venv
	uv pip install -r pyproject.toml --all-extras

cleanup: format lint typing ## format, lint, and type check

lint: ## lint the app using flake8 and ruff
	@echo "📝 linting..."
	uv run ruff check --fix

typing: ## type check the app using mypy
	@echo "📝 type checking..."
	uv run mypy src tests

test: ## test the app using pytest
	@echo "🧪 running test suite..."
	uv run pytest -vv --cov-report term-missing

format: ## runs cleaners
	@echo "🧾 formatting..."
	uv run ruff format

polish: cleanup test  ## cleans and lints before running the test suite

tox: ## runs linting, typechecking, and tests on all specified envs via tox
	@echo "🎯 tox..."
	uv run tox -p

##@ Build
build: cleanup test ## build the app package
	uv build

check_descr: ## check the app long description
	uvx twine check dist/*

##@ Release
release: ## release on pypi
	uvx twine upload dist/*
