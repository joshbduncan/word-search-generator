from __future__ import annotations

"""
    Word Search
    -----------
    Generate Word Search puzzles with Python.
    -----------
    :copyright: (c) 2021 Josh Duncan.
    :license: MIT, see LICENSE for more details.
"""

__app_name__ = "word-search"
__version__ = "3.1.0"


import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from . import export, generate, utils
from .config import (
    ACTIVE,
    INACTIVE,
    max_puzzle_size,
    max_puzzle_words,
    min_puzzle_size,
    min_puzzle_words,
)
from .mask import CompoundMask, Mask
from .word import Direction, KeyInfo, KeyInfoJson, Wordlist

Puzzle = List[List[str]]
DirectionSet = Set[Direction]
Key = Dict[str, KeyInfo]
KeyJson = Dict[str, KeyInfoJson]


class PuzzleNotGeneratedError(Exception):
    """For when a puzzle has yet to be generated."""

    pass


class PuzzleSizeError(Exception):
    """For when the length of each provided word is > `WordSearch.size`."""

    pass


class MissingWordError(Exception):
    """For when a `WordSearch` object cannot place all of its words."""

    pass


class WordSearch:
    """This class represents a WordSearch object."""

    def __init__(
        self,
        words: str | None = None,
        level: int | str | None = None,
        size: int | None = None,
        secret_words: str | None = None,
        secret_level: int | str | None = None,
        *,
        include_all_words: bool = False,
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
            include_all_words (bool, optional): Raises an error when _generate()
                cannot place all the words.  Secret words are not included in this
                check.
        """

        # setup puzzle
        self._puzzle: Puzzle = []
        self._size: int = 0
        self._masks: list[Any] = []
        self._mask: Puzzle = []
        self.force_all_words: bool = include_all_words

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
        self._secret_directions: DirectionSet = (
            utils.validate_level(secret_level) if secret_level else self.directions
        )

        if size:
            if not isinstance(size, int):
                raise TypeError("Size must be an integer.")
            if not min_puzzle_size <= size <= max_puzzle_size:
                raise ValueError(
                    f"Puzzle size must be >= {min_puzzle_size}"
                    + f" and <= {max_puzzle_size}."
                )
            self._size = size
        if self.words:
            self._size = utils.calc_puzzle_size(self._words, self._directions, size)
            self._generate()

    # **************************************************** #
    # ******************** PROPERTIES ******************** #
    # **************************************************** #

    @property
    def words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self._words}

    @property
    def placed_words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self._words if word.placed}

    @property
    def hidden_words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self._words if not word.secret}

    @property
    def placed_hidden_words(self) -> Wordlist:
        """The current puzzle words."""
        return {word for word in self.hidden_words if word.placed}

    @property
    def secret_words(self) -> Wordlist:
        """The current secret puzzle words."""
        return {word for word in self._words if word.secret}

    @property
    def placed_secret_words(self) -> Wordlist:
        """The current secret puzzle words."""
        return {word for word in self.secret_words if word.placed}

    @property
    def puzzle(self) -> Puzzle:
        """The current puzzle state."""
        return self._puzzle

    @property
    def solution(self) -> None:
        """Solution to the current puzzle state."""
        self.show(solution=True)

    @property
    def mask(self) -> Puzzle:
        """The current puzzle state."""
        return self._mask

    @property
    def masks(self) -> list[Mask]:
        """Puzzle masking status."""
        return self._masks

    @property
    def masked(self) -> bool:
        """Puzzle masking status."""
        return bool(self.masks)

    @property
    def bounding_box(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Bounding box of the active puzzle area."""
        return utils.find_bounding_box(self.mask)

    @property
    def cropped_puzzle(self) -> Puzzle:
        """The current puzzle state cropped to the mask."""
        min_x, min_y = self.bounding_box[0]
        max_x, max_y = self.bounding_box[1]
        return [
            [c for c in row[min_x : max_x + 1]]
            for row in self.puzzle[min_y : max_y + 1]
        ]

    @property
    def key(self) -> Key:
        """The current puzzle answer key (1-based) based from
        Position(0, 0) of the entire puzzle (not masked area)."""
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
                    word.text: word.key_info_json for word in self.words if word.placed
                },
            }
        )

    @property
    def unplaced_hidden_words(self) -> Wordlist:
        return self.hidden_words - self.placed_hidden_words

    @property
    def unplaced_secret_words(self) -> Wordlist:
        return self.secret_words - self.placed_secret_words

    # ********************************************************* #
    # ******************** GETTERS/SETTERS ******************** #
    # ********************************************************* #

    @property
    def directions(self) -> DirectionSet:
        """Valid directions for puzzle words."""
        return self._directions

    @directions.setter
    def directions(self, val: int | str | Iterable[str]):
        """Possible directions for puzzle words.

        Args:
            val (Union[int, str, Iterable[str]]): Either a preset puzzle level (int),
            cardinal directions as a comma separated string, or an iterable
            of valid directions from the Direction object.
        """
        self._directions = utils.validate_level(val)
        self._generate()

    def _set_level(self, val: int) -> None:
        """Set valid puzzle directions to a predefined level set.
        Here for backward compatibility."""
        if not isinstance(val, int):
            raise TypeError("Level must be an integer.")
        self._directions = utils.validate_level(val)

    def _get_level(self) -> DirectionSet:
        """Return valid puzzle directions. Here for backward compatibility."""
        return self.directions

    level = property(_get_level, _set_level, None, "Numeric setter for the level.")

    @property
    def secret_directions(self) -> DirectionSet:
        """Valid directions for secret puzzle words."""
        return self._secret_directions

    @secret_directions.setter
    def secret_directions(self, val: int | str | Iterable[str]):
        """Possible directions for secret puzzle words.

        Args:
            val (Union[int, str, Iterable[str]]): Either a preset puzzle level (int),
            valid cardinal directions as a comma separated string, or an iterable
            of valid cardinal directions.
        """
        self._secret_directions = utils.validate_level(val)
        self._generate()

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
        if not min_puzzle_size <= val <= max_puzzle_size:
            raise ValueError(
                f"Puzzle size must be >= {min_puzzle_size}"
                + f" and <= {max_puzzle_size}."
            )
        if self.size != val:
            self._size = val
            self._reapply_masks()
            self._generate()

    # ************************************************* #
    # ******************** METHODS ******************** #
    # ************************************************* #

    def random_words(
        self,
        count: int,
        action: str = "REPLACE",
        secret: bool = False,
        reset_size: bool = True,
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
                size based on the updated words. Defaults to True.

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

    def show(self, solution: bool = False) -> None:
        """Show the current puzzle with or without the solution.

        Args:
            solution (bool, optional): Highlight the puzzle solution. Defaults to False.
        """
        if self.key:
            print(utils.format_puzzle_for_show(self, solution))
        else:
            print("Empty puzzle.")

    def save(
        self,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
    ) -> str:
        """Save the current puzzle to a file.

        Args:
            path (Union[str, Path]): File save path.
            format (str, optional): Type of file to save ("CSV", "JSON", "PDF").
                Defaults to "PDF".
            solution (bool, optional): Include solution with the saved file.
                Only applies to PDF file type. Defaults to False.

        Returns:
            str: Final save path of the file.
        """
        if format.upper() not in ["CSV", "JSON", "PDF"]:
            raise ValueError('Save file format must be either "CSV", "JSON", or "PDF".')
        # validate export path
        path = export.validate_path(path)
        # write the file
        if format.upper() == "CSV":
            saved_file = export.write_csv_file(path, self)
        elif format.upper() == "JSON":
            saved_file = export.write_json_file(path, self)
        else:
            saved_file = export.write_pdf_file(path, self, solution)
        # return saved file path
        return str(saved_file)

    def reset_size(self):
        """Reset the puzzle size to the default setting
        (based on longest word length and total words)."""
        self.size = utils.calc_puzzle_size(self._words, self._directions)
        self._generate()

    # *************************************************************** #
    # ******************** PROCESSING/GENERATION ******************** #
    # *************************************************************** #

    def _generate(self, fill_puzzle: bool = True) -> None:
        """Generate the puzzle grid."""
        self._puzzle = utils.build_puzzle(self.size, "")
        min_word_length = (
            min([len(word.text) for word in self.words]) if self.words else self.size
        )
        if self.size < min_word_length:
            raise PuzzleSizeError
        for word in self.words:
            word.remove_from_puzzle()
        if not self.mask or len(self.mask) != self.size:
            self._mask = utils.build_puzzle(self.size, ACTIVE)
        if fill_puzzle:
            self._fill_puzzle()
        if self.force_all_words and self.unplaced_hidden_words:
            raise MissingWordError("All words could not be placed in the puzzle.")

    def _fill_puzzle(self) -> None:
        if self.words:
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

    def add_words(
        self, words: str, secret: bool = False, reset_size: bool = False
    ) -> None:
        """Add words to the puzzle.

        Args:
            words (str): Words to add.
            secret (bool, optional): Should the new words
                be secret. Defaults to False.
            reset_size (bool, optional): Reset the puzzle
                size based on the updated words. Defaults to False.
        """
        self._process_input(words, "add", secret)
        if reset_size:
            self.reset_size()
        else:
            self._generate()

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
        else:
            self._generate()

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
        else:
            self._generate()

    # ************************************************* #
    # ******************** MASKING ******************** #
    # ************************************************* #

    def apply_mask(self, mask: Mask) -> None:
        """Apply a singular mask object to the puzzle."""
        if not self.puzzle:
            raise PuzzleNotGeneratedError(
                "Puzzle not yet generated. Be sure to add puzzle `words` \
or set the puzzle `size` before applying a mask."
            )
        if not isinstance(mask, (Mask, CompoundMask)):
            raise TypeError("Please provide a Mask object.")
        if mask.puzzle_size != self.size:
            mask.generate(self.size)
        for y in range(self.size):
            for x in range(self.size):
                if mask.method == 1:
                    if mask.mask[y][x] == ACTIVE and self.mask[y][x] == ACTIVE:
                        self.mask[y][x] = ACTIVE
                    else:
                        self.mask[y][x] = INACTIVE
                elif mask.method == 2:
                    if mask.mask[y][x] == ACTIVE:
                        self.mask[y][x] = ACTIVE
                else:
                    if mask.mask[y][x] == ACTIVE:
                        self.mask[y][x] = INACTIVE
        # add mask to puzzle instance for later reference
        if mask not in self.masks:
            self.masks.append(mask)
        # fill in the puzzle
        self._generate()

    def apply_masks(self, masks: Iterable[Mask]) -> None:
        """Apply a group of masks to the puzzle."""
        for mask in masks:
            self.apply_mask(mask)

    def show_mask(self) -> None:
        """Show the current puzzle mask."""
        if self.masked:
            for row in self.mask:
                print(" ".join(row))
        else:
            print("Empty mask.")

    def invert_mask(self) -> None:
        """Invert the current puzzle mask. Has no effect on the
        actual mask(s) found in `WordSearch.mask`."""
        self._mask = [
            [ACTIVE if c == INACTIVE else INACTIVE for c in row] for row in self.mask
        ]
        self._generate()

    def flip_mask_horizontal(self) -> None:
        """Flip the current puzzle mask along the vertical axis (left to right).
        Has no effect on the actual mask(s) found in `WordSearch.mask`."""
        self._mask = [r[::-1] for r in self.mask]
        self._generate()

    def flip_mask_vertical(self) -> None:
        """Flip the current puzzle mask along the horizontal axis (top to bottom).
        Has no effect on the actual mask(s) found in `WordSearch.mask`."""
        self._mask = self.mask[::-1]
        self._generate()

    def transpose_mask(self) -> None:
        """Interchange each row with the corresponding column
        of the current puzzle mask. Has no effect on the actual
        mask(s) found in `WordSearch.mask`."""
        self._mask = list(map(list, zip(*self.mask)))
        self._generate()

    def remove_masks(self) -> None:
        """"""
        self._masks = []
        self._mask = utils.build_puzzle(self.size, ACTIVE)
        self._generate()

    def remove_static_masks(self) -> None:
        self._masks = [mask for mask in self.masks if not mask.static]

    def _reapply_masks(self) -> None:
        """Reapply all current masks to the puzzle."""
        self._mask = utils.build_puzzle(self.size, ACTIVE)
        for mask in self.masks:
            if mask.static and mask.puzzle_size != self.size:
                continue
            self.apply_mask(mask)

    # ******************************************************** #
    # ******************** DUNDER METHODS ******************** #
    # ******************************************************** #

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
            + f"{self.size}, "
            + f"'{','.join([word.text for word in self.secret_words])}',"
            + f"{utils.direction_set_repr(self.secret_directions)})"
        )

    def __str__(self):
        if self.key:
            return utils.format_puzzle_for_show(self)
        else:
            return "Empty puzzle."
