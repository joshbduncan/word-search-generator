from __future__ import annotations

import string
from abc import ABC, abstractmethod
from collections.abc import Iterable
from functools import wraps
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from collections.abc import Iterable

    from . import GameType
    from .game import Puzzle

WordFit: TypeAlias = tuple[str, list[tuple[int, int]]]
WordFits: TypeAlias = list[WordFit]

ALPHABET = list(string.ascii_uppercase)


class EmptyAlphabetError(Exception):
    """For when a `WordSearchGenerator` alphabet is empty."""

    def __init__(
        self, message="No valid alphabet characters provided to the generator."
    ):
        self.message = message
        super().__init__(self.message)


class WordFitError(Exception):
    """Raised when a word cannot be fit in the puzzle grid."""

    def __init__(self, message: str = "Word could not be fit in the puzzle grid"):
        self.message = message
        super().__init__(self.message)


def retry(retries: int = 1000):
    """Custom retry decorator for retrying a function `retries` times.

    Args:
        retries: Maximum number of retry attempts. Defaults to 1000.

    Returns:
        Decorator function that will retry the wrapped function on failure.
        Returns None if all retries are exhausted without success.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    continue

            # If we get here, all retries failed - return None gracefully
            return None

        return wrapper

    return decorator


class Generator(ABC):
    """Base class for the puzzle generation algorithm.

    To implement your own `Generator`, subclass this class and implement
    the required abstract methods. The generator handles the core logic
    of placing words in the puzzle grid and filling empty spaces.

    Example:
        ```python
        class CoolGenerator(Generator):
            def generate(self, game: Game) -> Puzzle:
                # Custom generation logic here
                return self._build_puzzle_grid(game)
        ```
    """

    def __init__(self, alphabet: str | Iterable[str] = ALPHABET) -> None:
        """Initialize a puzzle generator.

        Args:
            alphabet: Characters to use for puzzle filler. Can be a string
                or iterable of strings. Only alphabetic characters are kept.
                Defaults to A-Z.

        Raises:
            EmptyAlphabetError: If no valid alphabetic characters are provided.
        """
        if isinstance(alphabet, str):
            processed_chars = [c.upper() for c in alphabet if c.isalpha()]
        else:
            processed_chars = [
                c.upper() for c in alphabet if isinstance(c, str) and c.isalpha()
            ]

        # Remove duplicates while preserving order
        # Only fall back to default ALPHABET if alphabet parameter was the default
        if processed_chars:
            self.alphabet = list(dict.fromkeys(processed_chars))
        elif alphabet == ALPHABET:  # Only use default if explicitly passed the default
            self.alphabet = ALPHABET
        else:
            self.alphabet = []  # Empty if user provided invalid input

        if not self.alphabet:
            raise EmptyAlphabetError()

        # Validate minimum alphabet size for reasonable puzzle generation
        if len(self.alphabet) < 2:
            raise EmptyAlphabetError(
                "Alphabet must contain at least 2 unique characters"
            )

    @abstractmethod
    def generate(self, game: GameType) -> Puzzle:
        """Generate a puzzle grid with words placed according to game rules.

        This method must be implemented by subclasses to define the specific
        algorithm for placing words in the puzzle grid and filling remaining
        spaces with random characters from the alphabet.

        Args:
            game: The Game object containing words, size, and placement rules.

        Returns:
            A 2D list representing the completed puzzle grid with all words
            placed and remaining spaces filled with random characters.

        Raises:
            WordFitError: If words cannot be placed according to the constraints.
        """
