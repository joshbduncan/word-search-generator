"""
Word Search
-----------
Generate Word Search puzzles with Python.
-----------
:copyright: (c) 2025 Josh Duncan.
:license: MIT, see LICENSE for more details.
"""

__all__ = [
    "__version__",
    "WORD_LISTS",
    "WordSearch",
]

from rich.traceback import install

from .word_search.word_search import WordSearch
from .words import WORD_LISTS

install(show_locals=True)


def __getattr__(name: str) -> str:
    """Lazily get the version when needed."""

    if name == "__version__":
        from importlib.metadata import version

        return version("word_search_generator")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
