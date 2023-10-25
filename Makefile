VENV:=venv
BIN:=$(VENV)/bin
PWD := $(realpath $(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

.DEFAULT_GOAL := help
.PHONY: help
##@ General
help: ## Display this help section
	@echo $(MAKEFILE_LIST)
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

venv: requirements.txt ## build a virtual environment for development
	python -m venv $(VENV)
	$(BIN)/pip install -r requirements-dev.txt

##@ Development
venv_dev: requirements-dev.txt ## build a virtual environment for development
	python -m venv $(VENV)
	$(BIN)/pip install pip build
	$(BIN)/pip install -r requirements-dev.txt

cleanup: organize lint typing ## format, lint, and type check

lint: ## lint the app using flake8 and ruff
	@echo "📝 linting..."
	$(BIN)/flake8 src tests
	$(BIN)/ruff src tests

typing: ## type check the app using mypy
	@echo "📝 type checking..."
	$(BIN)/mypy src tests

test: ## test the app using pytest
	@echo "🧪 running test suite..."
	$(BIN)/pytest -vv --cov-report term-missing

organize: ## runs cleaners
	@echo "🧾 organizing..."
	$(BIN)/isort src tests
	$(BIN)/black src tests
	$(BIN)/ruff --fix src tests

polish: cleanup test  ## cleans and lints before running the test suite

##@ Build
build: cleanup ## build the app package
	$(BIN)/python -m build

check_descr: ## check the app long description
	$(BIN)/twine check dist/*

##@ Release
release: ## release on pypi
	$(BIN)/twine upload dist/*
