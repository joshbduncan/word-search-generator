from typing import TypeAlias

from .. import utils
from ..config import max_puzzle_words, min_puzzle_words
from ..formatter import WordSearchFormatter
from ..generator import WordSearchGenerator
from ..validator import NoPalindromes, NoPunctuation, NoSingleLetterWords, NoSubwords
from ..word import Direction, KeyInfo, KeyInfoJson
from . import Game

Puzzle: TypeAlias = list[list[str]]
DirectionSet: TypeAlias = set[Direction]
Key: TypeAlias = dict[str, KeyInfo]
KeyJson: TypeAlias = dict[str, KeyInfoJson]


class WordSearch(Game):
    """This class represents a WordSearch object."""

    DEFAULT_GENERATOR = WordSearchGenerator()
    DEFAULT_FORMATTER = WordSearchFormatter()
    DEFAULT_VALIDATORS = [
        NoPalindromes(),
        NoPunctuation(),
        NoSingleLetterWords(),
        NoSubwords(),
    ]

    def random_words(
        self,
        count: int,
        action: str = "REPLACE",
        secret: bool = False,
        reset_size: bool = False,
    ) -> None:
        """Add `count` randomly generated words to the puzzle.

        Args:
            count (int): Count of random words to add.
            action (str): Should the random words be added ("ADD") to the current
                wordlist or should they replace ("REPLACE") the current wordlist.
                Defaults to "REPLACE".
            secret (bool, optional): Should the new words
                be secret. Defaults to False.
            reset_size (bool, optional): Reset the puzzle
                size based on the updated words. Defaults to False.

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be greater than `config.min_puzzle_words` and
            less than `config.max_puzzle_words`.
        """
        if not isinstance(count, int):
            raise TypeError("Size must be an integer.")
        if not min_puzzle_words <= count <= max_puzzle_words:
            raise ValueError(
                f"Requested random words must be >= {min_puzzle_words}"
                + f" and <= {max_puzzle_words}."
            )
        if not isinstance(action, str):
            raise TypeError("Action must be a string.")
        if action.upper() not in ["ADD", "REPLACE"]:
            raise ValueError("Action must be either 'ADD' or 'REPLACE'.")
        if action.upper() == "ADD":
            self.add_words(
                ",".join(utils.get_random_words(count)),
                secret=secret,
                reset_size=reset_size,
            )
        else:
            self.replace_words(
                ",".join(utils.get_random_words(count)),
                secret=secret,
                reset_size=reset_size,
            )
