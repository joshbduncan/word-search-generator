"""
    Word Search
    -----------
    Generate Word Search puzzles with Python.
    -----------
    :copyright: (c) 2021 Josh Duncan.
    :license: MIT, see LICENSE for more details.
"""

__app_name__ = "word-search"
__version__ = "2.0.1"


import json
from pathlib import Path
from typing import Iterable, Optional, Union

from . import config, export, generate, utils
from .types import DirectionSet, Key, Puzzle, Wordlist


class WordSearch:
    """This class represents a WordSearch object."""

    def __init__(
        self,
        words: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        size: Optional[int] = None,
        secret_words: Optional[str] = None,
        secret_level: Optional[Union[int, str]] = None,
    ):
        """Initialize a Word Search puzzle.

        Args:
            words (Optional[str], optional): A string of words separated by spaces,
                commas, or new lines. Will be trimmed if more. Defaults to None.
            level (Optional[Union[int, str]], optional): Difficulty level or potential
                word directions. Defaults to 2.
            size (Optional[int], optional): Puzzle size. Defaults to None.
            secret_words (Optional[str], optional): A string of words separated by
                spaces, commas, or new lines. Words will be 'secret' meaning they
                will not be included in the word list. Defaults to None.
            secret_level (Optional[Union[int, str]], optional): Difficulty level or
                potential word directions for 'secret' words. Defaults to None.
        """

        # setup puzzle
        self._puzzle: Puzzle = []
        self._solution: Puzzle = []
        self._size: int = size if size else 0

        # setup words
        self._words: Wordlist = set()
        # in case of dupes, add secret words first so they are overwritten
        if secret_words:
            self._process_input(secret_words, "add", True)
        if words:
            self._process_input(words, "add")

        # determine valid directions
        self._directions: DirectionSet = (
            utils.validate_level(level) if level else utils.validate_level(2)
        )
        self._secret_directions: Optional[DirectionSet] = (
            utils.validate_level(secret_level) if secret_level else self.directions
        )

        if self.words:
            self._size = generate.calc_puzzle_size(self._words, self._directions, size)
            self._generate()

    @property
    def words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self._words}

    @property
    def placed_words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self._words if word.direction}

    @property
    def hidden_words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self._words if not word.secret}

    @property
    def placed_hidden_words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self.hidden_words if word.direction}

    @property
    def secret_words(self) -> Wordlist:
        """The current secret puzzle words."""
        return {word for word in self._words if word.secret}

    @property
    def placed_secret_words(self) -> Wordlist:
        """The current secret puzzle words."""
        return {word for word in self.secret_words if word.direction}

    @property
    def puzzle(self) -> Puzzle:
        """The current puzzle state."""
        return self._puzzle

    @property
    def solution(self) -> Puzzle:
        """Solution to the current puzzle state."""
        return self._solution

    @property
    def key(self) -> Key:
        """The current puzzle answer key (1-based)."""
        return {word.text: word.key_info for word in self.placed_words}

    @property
    def json(self) -> str:
        """The current puzzle, words, and answer key in JSON."""
        if not self.key:
            return json.dumps({})
        return json.dumps(
            {
                "puzzle": self.puzzle,
                "words": [word.text for word in self.placed_words],
                "key": {
                    word.text: word.key_info_json
                    for word in self.words
                    if word.direction
                },
            }
        )

    @property
    def directions(self) -> DirectionSet:
        """Valid directions for puzzle words."""
        return self._directions

    @directions.setter
    def directions(self, val: Union[int, str, Iterable[str]]):
        """Possible directions for puzzle words.

        Args:
            val (Union[int, str, Iterable[str]]): Either a preset puzzle level (int),
            cardinal directions as a comma separated string, or an iterable
            of valid directions from the Direction object.
        """
        self._directions = utils.validate_level(val)
        self._reset_puzzle()

    def _set_level(self, val: int) -> None:
        """Set valid puzzle directions to a predefined level set.
        Here for backward compatibility."""
        if not isinstance(val, int):
            raise TypeError("Level must be an integer.")
        self.directions = utils.validate_level(val)

    def _get_level(self) -> DirectionSet:
        """Return valid puzzle directions. Here for backward compatibility."""
        return self.directions

    level = property(_get_level, _set_level, None, "Numeric setter for the level.")

    @property
    def secret_directions(self):
        """Valid directions for secret puzzle words."""
        return self._secret_directions

    @secret_directions.setter
    def secret_directions(self, val: Union[int, str, Iterable[str]]):
        """Possible directions for secret puzzle words.

        Args:
            val (Union[int, str, Iterable[str]]): Either a preset puzzle level (int),
            valid cardinal directions as a comma separated string, or an iterable
            of valid cardinal directions.
        """
        if val:
            self._secret_directions = utils.validate_level(val)
        else:
            self._secret_directions = None
        self._reset_puzzle()

    @property
    def size(self) -> int:
        """Size (in characters) of the word search puzzle."""
        return self._size

    @size.setter
    def size(self, val: int):
        """Set the puzzle size. All puzzles are square.

        Args:
            val (int): Size in grid squares (characters).

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be greater than `config.min_puzzle_size` and
            less than `config.max_puzzle_size`.
        """
        if not isinstance(val, int):
            raise TypeError("Size must be an integer.")
        if not config.min_puzzle_size <= val <= config.max_puzzle_size:
            raise ValueError(
                f"Puzzle size must be >= {config.min_puzzle_size}"
                + f" and <= {config.max_puzzle_size}"
            )
        if self._size != val:
            self._size = val
            self._reset_puzzle()

    def reset_size(self):
        """Reset the puzzle size to the default setting
        (based on longest word length and total words)."""
        self._size = generate.calc_puzzle_size(self._words, self._directions)
        self._reset_puzzle()

    def _generate(self) -> None:
        generate.fill_words(self)
        if self.key:
            generate.fill_blanks(self)

    def _process_input(self, words: str, action: str = "add", secret: bool = False):
        if secret:
            clean_words = utils.cleanup_input(words, secret=True)
        else:
            clean_words = utils.cleanup_input(words)

        if action == "add":
            # remove all new words first so any updates are reflected in the word list
            self._words.symmetric_difference_update(clean_words)
            self._words.update(clean_words)
        if action == "remove":
            self._words.difference_update(clean_words)
        if action == "replace":
            self._words.clear()
            self._words.update(clean_words)

    def show(self, solution: bool = False) -> None:
        """Show the current puzzle with or without the solution.

        Args:
            solution (bool, optional): Highlight the puzzle solution. Defaults to False.
        """
        if self.key:
            print(utils.format_puzzle_for_show(self, solution))
        else:
            print("Empty puzzle.")

    def save(self, path: Union[str, Path], solution: bool = False) -> str:
        """Save the current puzzle to a file.

        Args:
            path (Union[str, Path]): A file save path
            solution (bool, optional): Include solution with the saved file.
                                       Defaults to False.

        Returns:
            str: Final save path of the file.
        """
        # check type of path provided
        if isinstance(path, Path):
            ftype = "csv" if ".csv" in path.name.lower() else "pdf"
        else:
            ftype = "csv" if ".csv" in path.lower() else "pdf"
        # validate export path
        path = export.validate_path(path)
        # write the file
        if ftype == "csv":
            saved_file = export.write_csv_file(path, self, solution)
        else:
            saved_file = export.write_pdf_file(path, self, solution)
        # return saved file path
        return str(saved_file)

    def add_words(
        self, words: str, secret: bool = False, reset_size: bool = False
    ) -> None:
        """Add words to the puzzle.

        Args:
            words (str): Words to remove.
            secret (bool, optional): Should the new words
            be secret. Defaults to False.
            reset_size (bool, optional): Reset the puzzle
            size based on the updated words. Defaults to False.
        """
        self._process_input(words, "add", secret)
        if reset_size:
            self.reset_size()
        self._reset_puzzle()

    def remove_words(self, words: str, reset_size: bool = False) -> None:
        """Remove words from the puzzle.

        Args:
            words (str): Words to remove.
            reset_size (bool, optional): Reset the puzzle
            size based on the updated words. Defaults to False.
        """
        self._process_input(words, "remove")
        if reset_size:
            self.reset_size()
        self._reset_puzzle()

    def replace_words(
        self, words: str, secret: bool = False, reset_size: bool = False
    ) -> None:
        """Replace all words from the puzzle.

        Args:
            words (str): Words to add.
            secret (bool, optional): Should the new words
            be secret. Defaults to False.
            reset_size (bool, optional): Reset the puzzle
            size based on the updated words. Defaults to False.
        """
        self._process_input(words, "replace", secret)
        if reset_size:
            self.reset_size()
        self._reset_puzzle()

    def _reset_puzzle(self):
        """Reset and regenerate the puzzle."""
        self._puzzle = []
        self._solution = []
        self._key = {}
        self._generate()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, WordSearch):
            return all(
                (
                    self.words == __o.words,
                    self.directions == __o.directions,
                    self.size == __o.size,
                    self.secret_words == __o.secret_words,
                    self.secret_directions == __o.secret_directions,
                )
            )
        return False

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            + f"('{','.join([word.text for word in self.hidden_words])}', "
            + f"{utils.direction_set_repr(self.directions)}, "
            + f"{self.size}, '{','.join([word.text for word in self.secret_words])}',"
            + f"{utils.direction_set_repr(self.secret_directions)})"
        )

    def __str__(self):
        if self.key:
            return utils.format_puzzle_for_show(self)
        else:
            return "Empty puzzle."
