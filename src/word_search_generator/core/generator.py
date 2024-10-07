from __future__ import annotations

import string
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, TypeAlias

if TYPE_CHECKING:  # pragma: no cover
    from . import GameType

from ..utils import Puzzle


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]

ALPHABET = list(string.ascii_uppercase)


class EmptyAlphabetError(Exception):
    """For when a `WordSearchGenerator` alphabet is empty."""

    def __init__(
        self, message="No valid alphabet characters provided to the generator."
    ):
        self.message = message
        super().__init__(self.message)


class WordFitError(Exception):
    pass


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

    def __init__(self, alphabet: str | Iterable[str] = ALPHABET) -> None:
        """Initialize a puzzle generator.

        Args:
            alphabet: Alphabet (letters) to use for the puzzle filler characters.
        """
        if alphabet:
            self.alphabet = list({c.upper() for c in alphabet if c.isalpha()})
        else:
            self.alphabet = ALPHABET

        if not self.alphabet:
            raise EmptyAlphabetError()

        self.puzzle: Puzzle = []

    @abstractmethod
    def generate(self, game: GameType) -> Puzzle:
        """Generate a puzzle.

        Args:
            game: The base `Game` object.

        Returns:
            The generated puzzle.
        """
