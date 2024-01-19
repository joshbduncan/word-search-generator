"""
    Word Search
    -----------
    Generate Word Search puzzles with Python.
    -----------
    :copyright: (c) 2024 Josh Duncan.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    "__version__",
    "WordSearch",
]

from .game.word_search import WordSearch  # noqa: F401c


def __getattr__(name: str) -> str:
    """Lazily get the version when needed."""

    if name == "__version__":
        from importlib.metadata import version

        return version("word_search_generator")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
