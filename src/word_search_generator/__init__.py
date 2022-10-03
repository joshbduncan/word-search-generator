# -*- coding: utf-8 -*-
"""
    Word Search
    -----------
    Generate Word Search puzzles with Python.
    -----------
    :copyright: (c) 2021 Josh Duncan.
    :license: MIT, see LICENSE for more details.
"""

__app_name__ = "word-search"
__version__ = "1.4.0"

import json
from pathlib import Path
from typing import Iterable, Union

from word_search_generator import config, export, generate, utils
from word_search_generator.types import DirectionSet, Key, Puzzle


class WordSearch:
    """This class represents a WordSearch object."""

    def __init__(
        self,
        words: str,
        level=None,
        size: int | None = None,
        secret_words: str | None = None,
        secret_level=None,
    ):
        """Initialize a Word Search puzzle.

        Args:
            words (str): words (str): A string of words separated by spaces, commas,
                or new lines and limited to 30 word max. Will be trimmed if more.
            level (Optional[int], optional): Difficulty level. Defaults to None.
            size (Optional[int], optional): Puzzle size. Defaults to None.
        """
        self.words = utils.cleanup_input(words)
        self.secret_words = (
            utils.cleanup_input(secret_words) - self.words if secret_words else set()
        )
        self._key: Key = {}
        # default to level 1 (E S) difficulty
        self._valid_directions: DirectionSet = utils.validate_level(1)
        self._secret_directions: DirectionSet | None = None
        self._puzzle: Puzzle = []
        self._size: int = 0
        self._solution: Puzzle = []

        # generate puzzle
        self.generate(level, size, secret_level)

    @property
    def puzzle(self) -> Puzzle:
        """The current puzzle state."""
        return self._puzzle

    @property
    def solution(self) -> Puzzle:
        """The solution to the current puzzle state."""
        return self._solution

    @property
    def key(self) -> Key:
        """The current puzzle answer key (1-based)."""
        return self._key

    @property
    def json(self) -> str:
        """The current puzzle, words, and answer key json."""
        return json.dumps(
            {
                "puzzle": self.puzzle,
                "words": list(self.words.union(self.secret_words)),
                "key": utils.get_answer_key_json(self.key),
            }
        )

    @property
    def valid_directions(self) -> DirectionSet:
        return self._valid_directions

    @valid_directions.setter
    def valid_directions(self, val: int | str | Iterable[str]):
        self._valid_directions = utils.validate_level(val)
        self._reset_puzzle()

    def _set_level(self, val: int) -> None:
        """Lvl should be an int, but putting that type hint in makes the linter upset"""
        try:
            self.valid_directions = utils.validate_level(val)
        except ValueError as e:  # extra work to pass tests
            if not isinstance(val, int):
                raise TypeError
            raise e

    def _get_level(self) -> DirectionSet:
        return self.valid_directions

    level = property(_get_level, _set_level, None, "Numeric setter for the level.")

    @property
    def secret_directions(self):
        return self._secret_directions

    @secret_directions.setter
    def secret_directions(self, val):
        if val:
            self._secret_directions = utils.validate_level(val)
        else:
            self._secret_directions = None
        self._reset_puzzle()

    @property
    def size(self) -> int:
        """The size of the word search puzzle."""
        return self._size

    @size.setter
    def size(self, val: int):
        """Set the size the puzzle. All puzzles are square.

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
        self._size = val
        self._reset_puzzle()

    def reset_size(self):
        """Reset the size to the default setting
        (based on longest word length and total words)."""
        self._size = 0
        self._reset_puzzle()

    def generate(
        self, level=None, size: int | None = None, secret_level=None
    ) -> Puzzle:
        """_summary_

        Args:
            level (Optional[int], optional): Difficulty level. Defaults to None.
            size (Optional[int], optional): Puzzle size. Defaults to None.
            secret_level: Difficulty of secret words.  Defaults to equal normal
                level difficulty.

        Returns:
            Puzzle: A newly generated puzzle.
        """
        if level:
            self.valid_directions = utils.validate_level(level)
        if size:
            self.size = size
        if secret_level:
            self.secret_directions = utils.validate_level(secret_level)

        self._solution, self._key = generate.fill_words(
            self.words,
            self.valid_directions,
            self.size,
            self.secret_words,
            self.secret_directions,
        )
        self._puzzle = generate.fill_blanks(self.solution, list(self.key.keys()))
        self._size = len(self._puzzle[0])

        return self.puzzle

    def show(self, solution: bool = False):
        """Show the current puzzle 'prettified' with or without the solution.

        Args:
            solution (bool, optional): Highlight the puzzle solution. Defaults to False.
        """
        if self._puzzle:
            print(
                utils.format_puzzle_for_show(
                    self.puzzle,
                    self.key,
                    self.valid_directions,
                    self.solution,
                    solution,
                )
            )

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

    def add_words(self, words: str, secret: bool = False) -> None:
        words_to_add = utils.cleanup_input(words)
        if secret:
            self.words = self.words - words_to_add
            self.secret_words.update(words_to_add)
        else:
            self.secret_words = self.secret_words - words_to_add
            self.words.update(words_to_add)
        self._reset_puzzle()

    def remove_words(self, words: str) -> None:
        words_to_remove = utils.cleanup_input(words)
        self.words = self.words - words_to_remove
        self.secret_words = self.secret_words - words_to_remove
        self._reset_puzzle()

    def replace_words(self, words: str) -> None:
        self.words = utils.cleanup_input(words)
        self._reset_puzzle()

    def _reset_puzzle(self):
        """Reset the puzzle after changes to attributes."""
        if self._puzzle:
            self._puzzle = []
            self._solution = []
            self._key = {}
            self.generate()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, WordSearch):
            return all(
                (
                    self.words == __o.words,
                    self.valid_directions == __o.valid_directions,
                    self.size == __o.size,
                    self.secret_words == __o.secret_words,
                    self.secret_directions == __o.secret_directions,
                )
            )
        return False

    def __repr__(self):
        words_str = ",".join(self.words)
        return (
            f"{self.__class__.__name__}('{words_str}', "  # ClassName & words
            + f"{utils.direction_set_repr(self.valid_directions)}, "  # directions
            + f"{self.size}, '{','.join(self.secret_words)}',"  # size+secrets
            + f"{utils.direction_set_repr(self.secret_directions)})"  # secret dirs
        )

    def __str__(self):
        return utils.format_puzzle_for_show(
            self.puzzle, self.key, self.valid_directions, self.solution
        )
