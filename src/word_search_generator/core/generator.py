from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:  # pragma: no cover
    from .game import Game, Puzzle


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]


class WordFitError(Exception):
    pass


def retry(retries: int = 1000):
    """Custom retry decorator for retrying a function `retries` times.

    Args:
        retries (int, optional): Retry attempts. Defaults to 1000.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempt += 1
            return

        return wrapper

    return decorator


class Generator(ABC):
    """Base class for the puzzle generation algorithm.

    To implement your own `Generator`, subclass this class.

    Example:
        ```python
        class CoolGenerator(Generator):
            def generate(self,  *args, **kwargs) -> Puzzle:
                ...
        ```
    """

    @abstractmethod
    def generate(self, game: Game) -> Puzzle:
        """Generate a puzzle.

        Args:
            game: The base `Game` object.

        Returns:
            The generated puzzle.
        """
