# Agent Guidelines for word-search-generator

## Build/Lint/Test Commands
- **Run all tests**: `make test` or `uv run pytest -vv --cov=src --cov-report term-missing`
- **Run single test**: `uv run pytest tests/test_filename.py::test_function_name -v`
- **Lint code**: `make lint` or `uv run ruff check --fix`
- **Format code**: `make format` or `uv run ruff format`
- **Type check**: `make typing` or `uv run mypy src tests && uv run ty check src tests`
- **Full cleanup**: `make cleanup` (format + lint + typing)
- **Build package**: `make build` or `uv build`

## Code Style Guidelines
- **Python version**: 3.11+ with full type hints required
- **Formatting**: ruff (88 char line length, double quotes, 4-space indentation)
- **Linting**: ruff with rules E, F, UP, B, SIM, I, C4, TCH
- **Type checking**: mypy with strict settings (no implicit optional, strict equality, etc.)
- **Imports**: stdlib → third-party → local, use `from __future__ import annotations`
- **Naming**: PascalCase classes, snake_case functions/variables, UPPER_CASE constants
- **Types**: Use `|` for unions, `collections.abc` for generics, `int | None` not `Optional[int]`
- **Docstrings**: Google-style with Args/Returns/Raises sections
- **Error handling**: Raise specific exceptions with descriptive messages
- **Security**: Never expose secrets/keys, follow security best practices
