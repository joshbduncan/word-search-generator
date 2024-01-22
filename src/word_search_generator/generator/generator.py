from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Iterable, TypeAlias

from ..config import max_fit_tries

if TYPE_CHECKING:  # pragma: no cover
    from ..game.game import DirectionSet, Puzzle
    from ..validator import Validator
    from ..word import WordSet


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]


class WordFitError(Exception):
    pass


def retry(retries: int = max_fit_tries):
    """Custom retry decorator for retrying a function `retries` times.

    Args:
        retries (int, optional): Retry attempts. Defaults to max_fit_tries.
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

    def __init__(self) -> None:
        self.puzzle: Puzzle = []

    @abstractmethod
    def generate(
        self,
        size: int,
        mask: Puzzle,
        words: WordSet,
        directions: DirectionSet,
        secret_directions: DirectionSet,
        validators: Iterable[Validator] | None,
        *args,
        **kwargs,
    ) -> Puzzle:
        """Generate a puzzle.

        Args:
            size (int): WordSearch size.
            mask (Puzzle): Current WordSearch mask.
            words (WordSet): WordSearch words to use for generation.
            directions (DirectionSet): Direction for hidden words.
            secret_directions (DirectionSet): Directions for secret words.
            validators (Iterable[Validator] | None, optional): Word validators.

        Returns:
            Puzzle: Generated puzzle.
        """
