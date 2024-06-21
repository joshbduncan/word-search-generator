import json
from math import log2
from pathlib import Path
from typing import Iterable, Sized, TypeAlias

from ..core.formatter import Formatter
from ..core.generator import Generator
from ..mask import CompoundMask, Mask
from ..utils import BoundingBox, find_bounding_box
from .directions import LEVEL_DIRS, Direction
from .validator import Validator
from .word import KeyInfo, KeyInfoJson, Word


class EmptyPuzzleError(Exception):
    """For when a `Game` puzzle is requested but is currently empty."""

    def __init__(self, message="Try adding words using the `add_words()` method."):
        self.message = message
        super().__init__(self.message)


class MissingGeneratorError(Exception):
    """For when a `Game` object doesn't have a generator specified."""

    def __init__(self, message="Generator required for puzzle generation."):
        self.message = message
        super().__init__(self.message)


class MissingFormatterError(Exception):
    """For when a `Game` object doesn't have a formatter specified."""

    def __init__(self, message="Formatter required for outputting the puzzle."):
        self.message = message
        super().__init__(self.message)


class PuzzleSizeError(ValueError):
    """For when a puzzle has an improper size."""

    pass


class EmptyWordlistError(Exception):
    """For when a `Game` object has no words."""

    pass


class NoValidWordsError(Exception):
    """For when a `Game` object has no valid words."""

    pass


class MissingWordError(Exception):
    """For when a `Game` object cannot place all of its words."""

    pass


Puzzle: TypeAlias = list[list[str]]
DirectionSet: TypeAlias = set[Direction]
Key: TypeAlias = dict[str, KeyInfo]
KeyJson: TypeAlias = dict[str, KeyInfoJson]
WordSet: TypeAlias = set[Word]


class Game:
    """Base object for a word base puzzle game."""

    MIN_PUZZLE_SIZE = 5
    MAX_PUZZLE_SIZE = 50
    MIN_PUZZLE_WORDS = 1
    MAX_PUZZLE_WORDS = 100
    MAX_FIT_TRIES = 1000

    DEFAULT_GENERATOR: Generator | None = None
    DEFAULT_FORMATTER: Formatter | None = None
    DEFAULT_VALIDATORS: Iterable[Validator] = []

    ACTIVE = "*"
    INACTIVE = "#"

    def __init__(
        self,
        words: str | WordSet | None = None,
        level: int | str | None = None,
        size: int | None = None,
        require_all_words: bool = False,
        generator: Generator | None = None,
        formatter: Formatter | None = None,
        validators: Iterable[Validator] | None = None,
    ):
        # setup puzzle
        self._words: WordSet = set()
        self._level: DirectionSet = set()
        self._size: int = size if size else 0
        self.require_all_words: bool = require_all_words

        self._puzzle: Puzzle = []
        self._masks: list[Mask] = []
        self._mask: Puzzle = []

        # setup required defaults
        self.generator: Generator | None = (
            generator if generator is not None else self.DEFAULT_GENERATOR
        )
        self.formatter: Formatter | None = (
            formatter if formatter is not None else self.DEFAULT_FORMATTER
        )
        self._validators: Iterable[Validator] | None = validators

        # set game words
        if words:
            self._words = (
                self._process_input(words) if isinstance(words, str) else words
            )

        # determine valid word directions
        self._directions: DirectionSet = (
            self.validate_level(level) if level else self.validate_level(2)
        )

        # calculate puzzle size
        if size:
            if not isinstance(size, int):
                raise TypeError("Size must be an integer.")
            if not self.MIN_PUZZLE_SIZE <= size <= self.MAX_PUZZLE_SIZE:
                raise ValueError(
                    f"Puzzle size must be >= {self.MIN_PUZZLE_SIZE}"
                    + f" and <= {self.MAX_PUZZLE_SIZE}."
                )
            self._size = size

        if self.words:
            self.generate()

    # **************************************************** #
    # ******************** PROPERTIES ******************** #
    # **************************************************** #

    @property
    def words(self) -> WordSet:
        """All puzzle words."""
        return set(self._words)

    @property
    def placed_words(self) -> WordSet:
        """Words of any type currently placed in the puzzle."""
        return {word for word in self.words if word.placed}

    @property
    def unplaced_words(self) -> WordSet:
        """Words of any type not currently placed in the puzzle."""
        return {word for word in self.words if not word.placed}

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
    def bounding_box(self) -> BoundingBox:
        """Bounding box of the active puzzle area as a rectangle defined
        by a tuple of (top-left edge as x, y, bottom-right edge as x, y)"""
        return find_bounding_box(self.mask, self.ACTIVE)

    @property
    def cropped_puzzle(self) -> Puzzle:
        """The current puzzle state cropped to the mask."""
        min_x, min_y = self.bounding_box[0]
        max_x, max_y = self.bounding_box[1]
        return [list(row[min_x : max_x + 1]) for row in self.puzzle[min_y : max_y + 1]]

    @property
    def cropped_size(self) -> tuple[int, int]:
        """Size (in characters) of `self.cropped_puzzle` as a (width, height) tuple."""
        return (len(self.cropped_puzzle[0]), len(self.cropped_puzzle))

    @property
    def key(self) -> Key:
        """The current puzzle answer key (1-based) based from
        Position(0, 0) of the entire puzzle (not masked area)."""
        return {word.text: word.key_info for word in self.placed_words}

    @property
    def json(self) -> str:
        """The current puzzle, and words in JSON."""
        if not self.puzzle or not self.placed_words:
            raise EmptyPuzzleError()
        return json.dumps(
            {
                "puzzle": self.cropped_puzzle,
                "words": [word.text for word in self.placed_words],
            }
        )

    # ********************************************************* #
    # ******************** GETTERS/SETTERS ******************** #
    # ********************************************************* #

    @property
    def directions(self) -> DirectionSet:
        """Valid directions for puzzle words."""
        return self._directions

    @directions.setter
    def directions(self, value: int | str | Iterable[str]):
        """Possible directions for puzzle words.

        Args:
            val: Either a preset puzzle level (int), cardinal directions
                as a comma separated string, or an iterable of valid directions
                from the Direction object.
        """
        self._directions = self.validate_level(value)
        self.generate()

    @property
    def direction_set_repr(self) -> str:
        """String representation of the game directions."""
        return (
            ("'" + ",".join(d.name for d in self.directions) + "'")
            if self.directions
            else "None"
        )

    def _set_level(self, value: int) -> None:
        """Set valid puzzle directions to a predefined level set.
        Here for backward compatibility."""
        if not isinstance(value, int):
            raise TypeError("Level must be an integer.")
        self._directions = self.validate_level(value)

    def _get_level(self) -> DirectionSet:
        """Return valid puzzle directions. Here for backward compatibility."""
        return self.directions

    level = property(_get_level, _set_level, None, "Numeric setter for the level.")

    @property
    def size(self) -> int:
        """Size (in characters) of the word search puzzle."""
        return self._size

    @size.setter
    def size(self, value: int):
        """Set the puzzle size. All puzzles are square.

        Args:
            val: Size in grid squares (characters).

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be greater than `self.MIN_PUZZLE_SIZE` and
                less than `self.MAX_PUZZLE_SIZE`.
        """
        if not isinstance(value, int):
            raise TypeError("Size must be an integer.")
        if not self.MIN_PUZZLE_SIZE <= value <= self.MAX_PUZZLE_SIZE:
            raise PuzzleSizeError(
                f"Puzzle size must be >= {self.MIN_PUZZLE_SIZE}"
                + f" and <= {self.MAX_PUZZLE_SIZE}."
            )
        if self.size != value:
            self._size = value
            self._reapply_masks()
            self.generate()

    @property
    def validators(self) -> Iterable[Validator] | None:
        """Game generation word validators."""
        return self._validators

    @validators.setter
    def validators(self, value: Iterable[Validator]) -> None:
        """Set validators for the game words.

        Args:
            value: Game word validators.
        """
        self._validators = value
        self.generate()

    # ************************************************* #
    # ******************** METHODS ******************** #
    # ************************************************* #

    def show(self, *args, **kwargs) -> None:
        """Show the current puzzle with or without the solution.

        Raises:
            EmptyPuzzleError: Puzzle not yet generated or puzzle has no placed words.
            MissingFormatterError: No puzzle formatter set.
        """
        if not self.puzzle or not self.placed_words:
            raise EmptyPuzzleError()
        if not self.formatter:
            raise MissingFormatterError()
        print(self.formatter.show(self, *args, **kwargs))

    def save(self, path: str | Path, format: str = "PDF", *args, **kwargs) -> str:
        """Save the current puzzle to a file.

        Args:
            path: File save path.
            format: Type of file to save ("CSV", "JSON", "PDF"). Defaults to "PDF".

        Raises:
            EmptyPuzzleError: Puzzle not yet generated or puzzle has no placed words.
            MissingFormatterError: No puzzle formatter set.

        Returns:
            Final save path of the file.
        """
        if not self.puzzle or not self.placed_words:
            raise EmptyPuzzleError()
        if not self.formatter:
            raise MissingFormatterError()
        return str(self.formatter.save(self, path, format, *args, **kwargs))

    # *************************************************************** #
    # ******************** PROCESSING/GENERATION ******************** #
    # *************************************************************** #

    @staticmethod
    def _build_puzzle(size: int, char: str) -> Puzzle:
        """Build an empty nested list/puzzle grid."""
        return [[char] * size for _ in range(size)]

    def generate(self, reset_size: bool = False) -> None:
        """Generate the puzzle grid.

        Args:
            reset_size: Recalculate the puzzle size before generation.
                Defaults to False.

        Raises:
            MissingGeneratorError: No set puzzle generator.
            EmptyWordlistError: No game words.
            PuzzleSizeError: Invalid puzzle size.
            NoValidWordsError: No valid game words.
            MissingWordError: Not all game words could be placed by the generator.
        """
        if not self.generator:
            raise MissingGeneratorError()
        if not self.words:
            raise EmptyWordlistError("No words have been added to the puzzle.")
        if not self.size or reset_size:
            self.size = self._calc_puzzle_size(self._words, self._directions)
        min_word_length = (
            min([len(word.text) for word in self.words]) if self.words else self.size
        )
        if self.size and self.size < min_word_length:
            raise PuzzleSizeError(
                f"Specified puzzle size `{self.size}` is smaller than shortest word."
            )
        for word in self.words:
            word.remove_from_puzzle()
        if not self.mask or len(self.mask) != self.size:
            self._mask = self._build_puzzle(self.size, self.ACTIVE)
        self._puzzle = self.generator.generate(self)
        if not self.masked and not self.placed_words:
            raise NoValidWordsError("No valid words have been added to the puzzle.")
        if self.require_all_words and self.unplaced_words:
            raise MissingWordError("All words could not be placed in the puzzle.")

    def _process_input(self, words: str, secret: bool = False) -> WordSet:
        clean_words = self._cleanup_input(words, secret=secret)
        return clean_words

    @staticmethod
    def _calc_puzzle_size(words: WordSet, level: Sized, size: int | None = None) -> int:
        """Calculate the puzzle grid size.

        Args:
            words: Game words.
            level: Game level.
            size: Set puzzle size. Defaults to None.

        Returns:
            Calculated puzzle size.
        """
        longest_word_length = len(max(words, key=len))
        if not size:
            longest = max(10, longest_word_length)
            # calculate multiplier for larger word lists so that most have room to fit
            multiplier = len(words) / 15 if len(words) > 15 else 1
            # level lengths in `core.directions` are nice multiples of 2
            l_size = log2(len(level)) if level else 1  # protect against log(0) in tests
            size = min(round(longest + l_size * 2 * multiplier), Game.MAX_PUZZLE_SIZE)
        return size

    def add_words(
        self,
        words: str | WordSet,
        secret: bool = False,
        reset_size: bool = False,
    ) -> None:
        """Add words to the puzzle.

        Args:
            words: Words to add.
            secret: Should the new words be secret. Defaults to False.
            reset_size: Reset the puzzle size based on the updated words.
                Defaults to False.
        """
        if isinstance(words, str):
            words = self._process_input(words, secret)

        # remove all new words first so any updates are reflected in the word list
        self._words.symmetric_difference_update(words)
        self._words.update(words)
        self.generate(reset_size=reset_size)

    def remove_words(self, words: str | WordSet, reset_size: bool = False) -> None:
        """Remove words from the puzzle.

        Args:
            words: Words to remove.
            reset_size: Reset the puzzle size based on the updated words.
                Defaults to False.
        """
        if isinstance(words, str):
            words = self._process_input(words)

        self._words.difference_update(words)
        self.generate(reset_size=reset_size)

    def replace_words(
        self, words: str | WordSet, secret: bool = False, reset_size: bool = False
    ) -> None:
        """Replace all words from the puzzle.

        Args:
            words: Words to add.
            secret: Should the new words be secret. Defaults to False.
            reset_size: Reset the puzzle size based on the updated words.
                Defaults to False.
        """
        if isinstance(words, str):
            words = self._process_input(words, secret)

        self._words.clear()
        self._words.update(words)
        self.generate(reset_size=reset_size)

    def _cleanup_input(self, words: str, secret: bool = False) -> WordSet:
        """Cleanup provided input string."""
        if not isinstance(words, str):
            raise TypeError(
                "Words must be a string separated by spaces, commas, or new lines"
            )
        # remove new lines
        words = words.replace("\n", ",")
        # remove excess spaces and commas
        word_list = ",".join(words.split(" ")).split(",")
        # iterate through all words and pick first set that match criteria
        word_set: WordSet = set()
        while word_list and len(word_set) <= self.MAX_PUZZLE_WORDS:
            word = word_list.pop(0)
            if word:
                word_set.add(Word(word, secret=secret))
        return word_set

    @staticmethod
    def _validate_direction_iterable(
        d: Iterable[str | tuple[int, int] | Direction]
    ) -> DirectionSet:
        """Validates that all the directions in d are found as keys to
        directions.dir_moves and therefore are valid directions."""
        o = set()
        for direction in d:
            if isinstance(direction, Direction):
                o.add(direction)
                continue
            elif isinstance(direction, tuple):
                o.add(Direction(direction))
                continue
            try:
                o.add(Direction[direction.upper().strip()])
            except KeyError:
                raise ValueError(f"'{direction}' is not a valid direction.")
        return o

    def validate_level(self, d) -> DirectionSet:
        """Given a d, try to turn it into a list of valid moves."""
        if isinstance(d, int):  # traditional numeric level
            try:
                return LEVEL_DIRS[d]
            except KeyError:
                raise ValueError(
                    f"{d} is not a valid difficulty number"
                    + f"[{', '.join([str(i) for i in LEVEL_DIRS])}]"
                )
        if isinstance(d, str):  # comma-delimited list
            return self._validate_direction_iterable(d.split(","))
        if isinstance(d, Iterable):  # probably used by external code
            if not d:
                raise ValueError("Empty iterable provided.")
            return self._validate_direction_iterable(d)
        raise TypeError(f"{type(d)} given, not str, int, or Iterable[str]\n{d}")

    # ************************************************* #
    # ******************** MASKING ******************** #
    # ************************************************* #

    def apply_mask(self, mask: Mask) -> None:
        """Apply a singular mask object to the puzzle."""
        if not self.puzzle:
            raise EmptyPuzzleError()
        if not isinstance(mask, (Mask, CompoundMask)):
            raise TypeError("Please provide a Mask object.")
        if mask.puzzle_size != self.size:
            mask.generate(self.size)
        for y in range(self.size):
            for x in range(self.size):
                if mask.method == 1:
                    if (
                        mask.mask[y][x] == self.ACTIVE
                        and self.mask[y][x] == self.ACTIVE
                    ):
                        self.mask[y][x] = self.ACTIVE
                    else:
                        self.mask[y][x] = self.INACTIVE
                elif mask.method == 2:
                    if mask.mask[y][x] == self.ACTIVE:
                        self.mask[y][x] = self.ACTIVE
                else:
                    if mask.mask[y][x] == self.ACTIVE:
                        self.mask[y][x] = self.INACTIVE
        # add mask to puzzle instance for later reference
        if mask not in self.masks:
            self.masks.append(mask)
        # fill in the puzzle
        self.generate()

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
            [self.ACTIVE if c == self.INACTIVE else self.INACTIVE for c in row]
            for row in self.mask
        ]
        self.generate()

    def flip_mask_horizontal(self) -> None:
        """Flip the current puzzle mask along the vertical axis (left to right).
        Has no effect on the actual mask(s) found in `WordSearch.mask`."""
        self._mask = [r[::-1] for r in self.mask]
        self.generate()

    def flip_mask_vertical(self) -> None:
        """Flip the current puzzle mask along the horizontal axis (top to bottom).
        Has no effect on the actual mask(s) found in `WordSearch.mask`."""
        self._mask = self.mask[::-1]
        self.generate()

    def transpose_mask(self) -> None:
        """Interchange each row with the corresponding column
        of the current puzzle mask. Has no effect on the actual
        mask(s) found in `WordSearch.mask`."""
        self._mask = list(map(list, zip(*self.mask)))
        self.generate()

    def remove_masks(self) -> None:
        self._masks = []
        self._mask = self._build_puzzle(self.size, self.ACTIVE)
        self.generate()

    def remove_static_masks(self) -> None:
        self._masks = [mask for mask in self.masks if not mask.static]

    def _reapply_masks(self) -> None:
        """Reapply all current masks to the puzzle."""
        self._mask = self._build_puzzle(self.size, self.ACTIVE)
        for mask in self.masks:
            if mask.static and mask.puzzle_size != self.size:
                continue
            self.apply_mask(mask)

    # ******************************************************** #
    # ******************** DUNDER METHODS ******************** #
    # ******************************************************** #

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Game):
            return all(
                (
                    self.words == __o.words,
                    self.directions == __o.directions,
                    self.size == __o.size,
                )
            )
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            + f"(words='{','.join([word.text for word in self.words])}', "
            + f"level={self.direction_set_repr}, "
            + f"size={self.size}, "
            + f"require_all_words={self.require_all_words})"
        )

    def __str__(self) -> str:
        if not self.puzzle or not self.formatter:
            return "Empty puzzle."
        return self.formatter.show(self)
