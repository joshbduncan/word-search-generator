# -*- coding: utf-8 -*-
"""
    Word Search
    -----------
    Generate Word Search puzzles with Python.
    -----------
    :copyright: (c) 2021 Josh Duncan.
    :license: MIT, see LICENSE for more details.
"""

__version__ = "1.0.7"

from typing import Optional, Set
from word_search_generator import config
from word_search_generator import export
from word_search_generator import generate
from word_search_generator.types import Key, Puzzle, SavePath
from word_search_generator import utils


class WordSearch:
    """This class represents a WordSearch object
    used for generating Word Search puzzles."""

    def __init__(
        self, words: str, level: Optional[int] = None, size: Optional[int] = None
    ):
        """Initializa a Word Search puzzle.

        Args:
            words (str): A string of words separated by spaces, commas, or
            new lines and limited to 30 word max. Will be trimmed if more.
            level (Optional[int], optional): Difficulty level. Defaults to None.
            size (Optional[int], optional): Puzzle size. Defaults to None.
        """
        self.words = utils.cleanup_input(words)
        self._key: Key = {}
        self._level: int = 1
        self._puzzle: Puzzle = []
        self._size: int = 10
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
        """The current puzzle answer key."""
        return self._key

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
        """Generate a word search puzzle using `self.words`.

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
        self._puzzle = generate.fill_blanks(self._solution)

        return self.puzzle

    def show(self, key: bool = False, solution: bool = False, tabs: bool = False):
        """Show the current puzzle.

        Args:
            key (bool, optional): Show solution key. Defaults to False.
            solution (bool, optional): Show only the hidden words. Defaults to False.
            tabs (bool, optional): Use tabs between characters. Defaults to False.
        """
        if solution:
            print(utils.stringify(self.solution, tabs=tabs))
        else:
            print("** WORD SEARCH **\n")
            print(utils.stringify(self.puzzle, tabs=tabs))
            print(f"\nFind these words: {', '.join(sorted(self.words))}")
            print(f"* Words can go {utils.get_level_dirs_str(self.level)}.")
            if key:
                print(f"\nAnswer Key: {utils.get_answer_key_str(self.key)}")

    def save(self, path: SavePath = None, format: str = "pdf") -> str:
        """Save the current puzzle to a file.

        Args:
            path (SavePath, optional): A filename (string) or
            pathlib.Path object. Defaults to None.
            format (str, optional): Save file format (csv or pdf). Defaults to "pdf".

        Raises:
            ValueError: Format must be either 'csv' or 'pdf'.

        Returns:
            str: Final save path of the file.
        """
        # check validity of format
        if format.lower() not in ["csv", "pdf"]:
            raise ValueError("Format must be either 'csv' or 'pdf'")
        ftype = ".pdf" if format.lower() == "pdf" else ".csv"
        # validate export path
        fpath = export.validate_path(path, ftype)
        # write the file
        if ftype == ".csv":
            saved_file = export.write_csv_file(fpath, self.puzzle, self.key, self.level)
        else:
            saved_file = export.write_pdf_file(fpath, self.puzzle, self.key, self.level)
        # return saved file path
        return str(saved_file)

    def add_words(self, words: str) -> Set[str]:
        """Add new words to the puzzle.

        Args:
            words (str): A string of words separated by spaces, commas, or new lines.

        Returns:
            Set[str]: An updated set of words.
        """
        self.words.update(utils.cleanup_input(words))
        self._reset_puzzle()

        return self.words

    def remove_words(self, words: str) -> Set[str]:
        """Remove words from the puzzle.

        Args:
            words (str): A string of words separated by spaces, commas, or new lines.

        Returns:
            Set[str]: An updated set of words.
        """
        removals = utils.cleanup_input(words)
        self.words = self.words - removals
        self._reset_puzzle()
        return self.words

    def replace_words(self, words: str):
        """Replace all words in the puzzle.

        Args:
            words (str): A string of words separated by spaces, commas, or new lines.

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

    def __repr__(self):
        return f"WordSearch('{self.words}')"

    def __str__(self):
        return utils.stringify(self.puzzle)
