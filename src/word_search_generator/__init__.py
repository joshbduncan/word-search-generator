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
__version__ = "1.3.0"

import json
from pathlib import Path
from typing import Optional, Union

from word_search_generator import config, export, generate, utils
from word_search_generator.types import Key, Puzzle


class WordSearch:
    """This class represents a WordSearch object."""

    def __init__(
        self, words: str, level: Optional[int] = None, size: Optional[int] = None
    ):
        """Initializa a Word Search puzzle.

        Args:
            words (str): words (str): A string of words separated by spaces, commas,
            or new lines and limited to 30 word max. Will be trimmed if more.
            level (Optional[int], optional): Difficulty level. Defaults to None.
            size (Optional[int], optional): Puzzle size. Defaults to None.
        """
        self.words = utils.cleanup_input(words)
        self._key: Key = {}
        self._level: int = 1
        self._puzzle: Puzzle = []
        self._size: int = 0
        self._solution: Puzzle = []
        # generate puzzle
        self.generate(level, size)

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
                "words": list(self.words),
                "key": utils.get_answer_key_json(self.key),
            }
        )

    @property
    def level(self) -> int:
        """The difficulty level of the puzzle."""
        return self._level

    @level.setter
    def level(self, val: int):
        """Set the difficulty level of the word search.

        Level 1 (Easy): Words can go forward in directions
        EAST (E), or SOUTH (S).
        Puzzle size is small by default.

        Level 2 (Intermediate): Words can go forward in directions
        NORTHEAST (NE), EAST (E), SOUTHEAST (SE), or (S).
        Puzzle size is medium by default.

        Level 3 (Expert): Words can go forward and backwards in directions
        NORTH (N), NORTHEAST (NE), EAST (E), SOUTHEAST (SE),
        SOUTH (S), SOUTHWEST (SW), WEST (W), or NORTHWEST (NW).
        Puzzle size is large by default.

        Args:
            val (int): An integer of 1, 2, or 3.

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be 1, 2, or 3.
        """
        if not isinstance(val, int):
            raise TypeError("Level must be an integer.")
        if val not in [1, 2, 3]:
            raise ValueError("Level must be 1, 2, or 3.")
        self._level = val
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
        self, level: Optional[int] = None, size: Optional[int] = None
    ) -> Puzzle:
        """_summary_

        Args:
            level (Optional[int], optional): Difficulty level. Defaults to None.
            size (Optional[int], optional): Puzzle size. Defaults to None.

        Returns:
            Puzzle: A newly generated puzzle.
        """
        if level:
            self.level = level
        if size:
            self.size = size

        self._solution, self._key = generate.fill_words(
            self.words, self.level, self.size
        )
        self._puzzle = generate.fill_blanks(self.solution, list(self.key.keys()))
        self._size = len(self._puzzle[0])

        return self.puzzle

    def show(self, solution: bool = False):
        """Show the current puzzle 'prettified' with or without the solution.

        Args:
            solution (bool, optional): Highlight the puzzle solution. Defaults to False.
        """
        print(
            utils.format_puzzle_for_show(
                self.puzzle, self.key, self.level, self.solution, solution
            )
        )

    def save(self, path: Union[str, Path]) -> str:
        """Save the current puzzle to a file.

        Args:
            path (Union[str, Path]): A file save path.

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
            saved_file = export.write_csv_file(path, self.puzzle, self.key, self.level)
        else:
            saved_file = export.write_pdf_file(path, self.puzzle, self.key, self.level)
        # return saved file path
        return str(saved_file)

    def add_words(self, words: str) -> set[str]:
        """Add new words to the puzzle.

        Args:
            words (str): A string of words separated by
            spaces, commas, or new lines.

        Returns:
            set[str]: An updated set of words.
        """
        # self.words.update(utils.cleanup_input(words))
        old_words = ", ".join(self.words)
        combined_words = old_words + "," + words
        self.words = utils.cleanup_input(combined_words)
        self._reset_puzzle()
        return self.words

    def remove_words(self, words: str) -> set[str]:
        """Remove words from the puzzle.

        Args:
            words (str): A string of words separated by
            spaces, commas, or new lines.

        Returns:
            set[str]: An updated set of words.
        """
        removals = utils.cleanup_input(words)
        self.words = self.words - removals
        self._reset_puzzle()
        return self.words

    def replace_words(self, words: str):
        """Replace all words in the puzzle.

        Args:
            words (str): A string of words separated by
            spaces, commas, or new lines.

        Returns:
            [type]: An updated set of words.
        """
        self.words = utils.cleanup_input(words)
        self._reset_puzzle()
        return self.words

    def _reset_puzzle(self):
        """Reset the puzzle after changes to attributes."""
        if self._puzzle:
            self._puzzle = []
            self._solution = []
            self._key = {}
            self.generate()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, WordSearch):
            words = self.words == __o.words
            level = self.level == __o.level
            size = self.size == __o.size
            return all([words, level, size])
        return False

    def __repr__(self):
        words_str = ",".join(self.words)
        return f"{self.__class__.__name__}('{words_str}', {self.level}, {self.size})"

    def __str__(self):
        return utils.format_puzzle_for_show(
            self.puzzle, self.key, self.level, self.solution
        )
