import json
from pathlib import Path
from typing import Iterable, TypeAlias

from .. import config, utils
from ..formatter import Formatter
from ..generator import Generator
from ..mask import CompoundMask, Mask
from ..validator import Validator
from ..word import Direction, KeyInfo, KeyInfoJson, Word, WordSet

Puzzle: TypeAlias = list[list[str]]
DirectionSet: TypeAlias = set[Direction]
Key: TypeAlias = dict[str, KeyInfo]
KeyJson: TypeAlias = dict[str, KeyInfoJson]


class EmptyPuzzleError(Exception):
    """For when a `Game` puzzle is requested but is currently empty."""

    def __init__(self, message="Try adding words using the `add_words()` method."):
        self.message = message
        super().__init__(self.message)


class MissingGeneratorError(Exception):
    """For when a `Game` object doesn't have a generator specified."""

    def __init__(self, message="Generator required to puzzle generation."):
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


class MissingWordError(Exception):
    """For when a `Game` object cannot place all of its words."""

    pass


class Game:
    """Base object for a word base puzzle game."""

    DEFAULT_GENERATOR: Generator | None = None
    DEFAULT_FORMATTER: Formatter | None = None
    DEFAULT_VALIDATORS: Iterable[Validator] = []

    def __init__(
        self,
        words: str | None = None,
        level: int | str | None = None,
        size: int | None = None,
        secret_words: str | None = None,
        secret_level: int | str | None = None,
        *,
        include_all_words: bool = False,
        generator: Generator | None = None,
        formatter: Formatter | None = None,
        validators: Iterable[Validator] | None = None,
    ):
        """Initialize a game.

        Args:
            words (str | None, optional): A string of words separated by spaces,
                commas, or new lines. Will be trimmed if more. Defaults to None.
            level (int | str | None, optional): Difficulty level or potential
                word directions. Defaults to 2.
            size (int | None, optional): Puzzle size. Defaults to None.
            secret_words (str | None, optional): A string of words separated by
                spaces, commas, or new lines. Words will be 'secret' meaning they
                will not be included in the word list. Defaults to None.
            secret_level (int | str | None, optional): Difficulty level or
                potential word directions for 'secret' words. Defaults to None.
            include_all_words (bool, optional): Raises an error when `generator`
                cannot place all the words.  Secret words are not included in this
                check.
            generator (Generator | None, optional): Puzzle generator. Defaults to None.
            formatter (Formatter | None, optional): Game formatter. Defaults to None.
            validators (Iterable[Validator] | None, optional): An iterable
            of validators that puzzle words will be checked against during puzzle
            generation. Provide an empty iterable to disable word validation.
            Defaults to `DEFAULT_VALIDATORS`.
        """
        # setup puzzle
        self._words: WordSet = set()
        self._puzzle: Puzzle = []
        self._size: int = 0
        self._masks: list[Mask] = []
        self._mask: Puzzle = []
        self.force_all_words: bool = include_all_words
        self.generator: Generator | None = generator
        self.formatter: Formatter | None = formatter
        self._validators: Iterable[Validator] = (
            validators if validators else self.DEFAULT_VALIDATORS
        )

        # setup words
        # in case of dupes, add secret words first so they are overwritten
        if secret_words:
            self._process_input(secret_words, "add", True)
        if words:
            self._process_input(words, "add")

        # determine valid directions
        self._directions: DirectionSet = (
            self.validate_level(level) if level else self.validate_level(2)
        )
        self._secret_directions: DirectionSet = (
            self.validate_level(secret_level) if secret_level else self.directions
        )

        # setup required defaults
        if not self.generator:
            self.generator = self.DEFAULT_GENERATOR
        if not self.formatter:
            self.formatter = self.DEFAULT_FORMATTER

        # generate puzzle
        if size:
            if not isinstance(size, int):
                raise TypeError("Size must be an integer.")
            if not config.min_puzzle_size <= size <= config.max_puzzle_size:
                raise ValueError(
                    f"Puzzle size must be >= {config.min_puzzle_size}"
                    + f" and <= {config.max_puzzle_size}."
                )
            self._size = size
        if self.words:
            self._size = utils.calc_puzzle_size(self.words, self.directions, self.size)
            self._generate()

    # **************************************************** #
    # ******************** PROPERTIES ******************** #
    # **************************************************** #

    @property
    def words(self) -> WordSet:
        """The current puzzle words."""
        return set(self._words)

    @property
    def placed_words(self) -> WordSet:
        """The current puzzle words."""
        return {word for word in self._words if word.placed}

    @property
    def hidden_words(self) -> WordSet:
        """The current puzzle words."""
        return {word for word in self._words if not word.secret}

    @property
    def placed_hidden_words(self) -> WordSet:
        """The current puzzle words."""
        return {word for word in self.hidden_words if word.placed}

    @property
    def secret_words(self) -> WordSet:
        """The current secret puzzle words."""
        return {word for word in self._words if word.secret}

    @property
    def placed_secret_words(self) -> WordSet:
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
        """Bounding box of the active puzzle area as a rectangle defined
        by a tuple of (top-left edge as x, y, bottom-right edge as x, y)"""
        return utils.find_bounding_box(self.mask)

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
        """The current puzzle, words, and answer key in JSON."""
        if not self.key:
            return json.dumps({})
        return json.dumps(
            {
                "puzzle": self.cropped_puzzle,
                "words": [word.text for word in self.placed_words],
                "key": {
                    word.text: word.key_info_json for word in self.words if word.placed
                },
            }
        )

    @property
    def unplaced_hidden_words(self) -> WordSet:
        return self.hidden_words - self.placed_hidden_words

    @property
    def unplaced_secret_words(self) -> WordSet:
        return self.secret_words - self.placed_secret_words

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
            val (int | str | Iterable[str]): Either a preset puzzle level (int),
            cardinal directions as a comma separated string, or an iterable
            of valid directions from the Direction object.
        """
        self._directions = self.validate_level(value)
        self._generate()

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
    def secret_directions(self) -> DirectionSet:
        """Valid directions for secret puzzle words."""
        return self._secret_directions

    @secret_directions.setter
    def secret_directions(self, value: int | str | Iterable[str]):
        """Possible directions for secret puzzle words.

        Args:
            val (int | str | Iterable[str]): Either a preset puzzle level (int),
            valid cardinal directions as a comma separated string, or an iterable
            of valid cardinal directions.
        """
        self._secret_directions = self.validate_level(value)
        self._generate()

    @property
    def size(self) -> int:
        """Size (in characters) of the word search puzzle."""
        return self._size

    @size.setter
    def size(self, value: int):
        """Set the puzzle size. All puzzles are square.

        Args:
            val (int): Size in grid squares (characters).

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be greater than `config.config.min_puzzle_size` and
            less than `config.config.max_puzzle_size`.
        """
        if not isinstance(value, int):
            raise TypeError("Size must be an integer.")
        if not config.min_puzzle_size <= value <= config.max_puzzle_size:
            raise PuzzleSizeError(
                f"Puzzle size must be >= {config.min_puzzle_size}"
                + f" and <= {config.max_puzzle_size}."
            )
        if self.size != value:
            self._size = value
            self._reapply_masks()
            self._generate()

    @property
    def validators(self) -> Iterable[Validator]:
        """Puzzle generation word validators."""
        return self._validators

    @validators.setter
    def validators(self, value: Iterable[Validator]) -> None:
        self._validators = value
        self._generate()

    # ************************************************* #
    # ******************** METHODS ******************** #
    # ************************************************* #

    def show(
        self, solution: bool = False, hide_fillers: bool = False, *args, **kwargs
    ) -> None:
        """Show the current puzzle with or without the solution.

        Args:
            solution (bool, optional): Highlight the puzzle solution. Defaults to False.
            hide_fillers (bool, optional): Hide all filler letters so only the solution
                is shown. Overrides `solution`. Defaults to False.
        """
        if not self.key:
            raise EmptyPuzzleError()
        if not self.formatter:
            if not self.DEFAULT_FORMATTER:
                raise MissingFormatterError()
            self.formatter = self.DEFAULT_FORMATTER
        print(self.formatter.show(self, solution, hide_fillers, *args, **kwargs))

    def save(
        self,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
        *args,
        **kwargs,
    ) -> str:
        """Save the current puzzle to a file.

        Args:
            path (str | Path): File save path.
            format (str, optional): Type of file to save ("CSV", "JSON", "PDF").
                Defaults to "PDF".
            solution (bool, optional): Include solution with the saved file.
                For CSV and JSON files, only placed word characters will be included.
                For PDF, a separate solution page will be included with word
                characters highlighted in red. Defaults to False.

        Returns:
            str: Final save path of the file.
        """
        if not self.key:
            raise AttributeError("No puzzle data to save.")
        if not self.formatter:
            if not self.DEFAULT_FORMATTER:
                raise MissingFormatterError()
            self.formatter = self.DEFAULT_FORMATTER
        return str(self.formatter.save(self, path, format, solution, *args, **kwargs))

    # *************************************************************** #O
    # ******************** PROCESSING/GENERATION ******************** #
    # *************************************************************** #

    def _generate(self, reset_size: bool = False) -> None:
        """Generate the puzzle grid."""
        # if an empty puzzle object is created then the `random_words()` method
        # is called, calculate an appropriate puzzle size
        if not self.generator:
            if not self.DEFAULT_GENERATOR:
                raise MissingGeneratorError()
            self.generator = self.DEFAULT_GENERATOR
        self._puzzle = []
        if not self.words:
            return
        if not self.size or reset_size:
            self.size = utils.calc_puzzle_size(self._words, self._directions)
        min_word_length = (
            min([len(word.text) for word in self.words]) if self.words else self.size
        )
        if self.size and self.size < min_word_length:
            raise PuzzleSizeError(
                "Specified puzzle size `{self.size}` is smaller than shortest word."
            )
        for word in self.words:
            word.remove_from_puzzle()
        if not self.mask or len(self.mask) != self.size:
            self._mask = utils.build_puzzle(self.size, config.ACTIVE)
        self._puzzle = self.generator.generate(
            self.size,
            self.mask,
            self.words,
            self.directions,
            self.secret_directions,
            self.validators,
        )
        if self.force_all_words and self.unplaced_hidden_words:
            raise MissingWordError("All words could not be placed in the puzzle.")

    def _process_input(self, words: str, action: str = "add", secret: bool = False):
        if secret:
            clean_words = self.cleanup_input(words, secret=True)
        else:
            clean_words = self.cleanup_input(words)

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
        self._generate(reset_size=reset_size)

    def remove_words(self, words: str, reset_size: bool = False) -> None:
        """Remove words from the puzzle.

        Args:
            words (str): Words to remove.
            reset_size (bool, optional): Reset the puzzle
                size based on the updated words. Defaults to False.
        """
        self._process_input(words, "remove")
        self._generate(reset_size=reset_size)

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
        self._generate(reset_size=reset_size)

    def cleanup_input(self, words: str, secret: bool = False) -> WordSet:
        """Cleanup provided input string. Removing spaces
        one-letter words, and words with punctuation."""
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
        while word_list and len(word_set) <= config.max_puzzle_words:
            word = word_list.pop(0)
            if word:
                word_set.add(Word(word, secret=secret))
        return word_set

    def validate_direction_iterable(
        self, d: Iterable[str | tuple[int, int] | Direction]
    ) -> DirectionSet:
        """Validates that all the directions in d are found as keys to
        config.dir_moves and therefore are valid directions."""
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
                return config.level_dirs[d]
            except KeyError:
                raise ValueError(
                    f"{d} is not a valid difficulty number"
                    + f"[{', '.join([str(i) for i in config.level_dirs])}]"
                )
        if isinstance(d, str):  # comma-delimited list
            return self.validate_direction_iterable(d.split(","))
        if isinstance(d, Iterable):  # probably used by external code
            if not d:
                raise ValueError("Empty iterable provided.")
            return self.validate_direction_iterable(d)
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
                        mask.mask[y][x] == config.ACTIVE
                        and self.mask[y][x] == config.ACTIVE
                    ):
                        self.mask[y][x] = config.ACTIVE
                    else:
                        self.mask[y][x] = config.INACTIVE
                elif mask.method == 2:
                    if mask.mask[y][x] == config.ACTIVE:
                        self.mask[y][x] = config.ACTIVE
                else:
                    if mask.mask[y][x] == config.ACTIVE:
                        self.mask[y][x] = config.INACTIVE
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
            [config.ACTIVE if c == config.INACTIVE else config.INACTIVE for c in row]
            for row in self.mask
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
        self._mask = utils.build_puzzle(self.size, config.ACTIVE)
        self._generate()

    def remove_static_masks(self) -> None:
        self._masks = [mask for mask in self.masks if not mask.static]

    def _reapply_masks(self) -> None:
        """Reapply all current masks to the puzzle."""
        self._mask = utils.build_puzzle(self.size, config.ACTIVE)
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
                    self.secret_words == __o.secret_words,
                    self.secret_directions == __o.secret_directions,
                )
            )
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            + f"(words='{','.join([word.text for word in self.hidden_words])}', "
            + f"level={utils.direction_set_repr(self.directions)}, "
            + f"size={self.size}, "
            + f"secret_words='{','.join([word.text for word in self.secret_words])}', "
            + f"secret_level={utils.direction_set_repr(self.secret_directions)}, "
            + f"include_all_words={self.force_all_words})"
        )

    def __str__(self) -> str:
        if not self.key:
            raise EmptyPuzzleError()
        elif not self.generator:
            raise MissingGeneratorError()
        elif not self.formatter:
            raise MissingFormatterError()
        return self.formatter.show(self)
