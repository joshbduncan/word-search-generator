from nox import Session, options
from nox_uv import session

options.default_venv_backend = "uv"


@session(
    python=["3.10", "3.11", "3.12", "3.13"],
    uv_groups=["test"],
    reuse_venv=True,
)
def test(s: Session) -> None:
    s.run("pytest")


@session(
    uv_groups=["types"],
    reuse_venv=True,
)
def types(s: Session) -> None:
    s.run("mypy", "src", "tests")


@session(
    uv_only_groups=["lint"],
    reuse_venv=True,
)
def lint_and_format(s: Session) -> None:
    s.run("ruff", "check")
    s.run("ruff", "format")
