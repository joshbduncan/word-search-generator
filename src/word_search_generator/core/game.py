"""Word search puzzle game engine.

This module provides the core Game class for creating, managing, and manipulating
word search puzzles. The Game class serves as the central orchestrator that combines
words, generators, formatters, validators, and masks to create complete word search
puzzles.

Key Concepts:
    - Game: Main class that manages the entire puzzle lifecycle
    - Puzzle: The letter grid containing placed words and filler characters
    - Mask: Optional shapes that constrain where words can be placed
    - Generator: Algorithm for placing words and filling empty spaces
    - Formatter: Output handler for displaying or saving puzzles
    - Validator: Rules engine for filtering valid words

Architecture:
    The Game class follows a component-based design where different aspects
    of puzzle creation are handled by specialized components:

    1. Word Management: Add, remove, and validate words
    2. Grid Generation: Place words using configurable algorithms
    3. Masking System: Apply geometric constraints to puzzle shapes
    4. Output Control: Format and export puzzles in various formats
    5. Validation Framework: Ensure word quality and puzzle constraints

Example:
    Basic puzzle creation:

    >>> game = Game(words="cat dog bird", level=2, size=15)
    >>> game.show()  # Display the puzzle
    >>> game.save("puzzle.pdf")  # Export to PDF

Dependencies:
    - Generator: Handles word placement algorithms
    - Formatter: Manages puzzle display and export
    - Validator: Applies word filtering rules
    - Mask: Defines puzzle shape constraints
    - Word: Represents individual puzzle words with metadata
"""

import json
from collections.abc import Iterable, Sized
from math import log2
from pathlib import Path
from typing import TypeAlias

from ordered_set import OrderedSet

from ..core.formatter import ExportFormat, Formatter
from ..core.generator import Generator
from ..mask import CompoundMask, Mask
from ..utils import BoundingBox, find_bounding_box
from .directions import LEVEL_DIRS, Direction
from .validator import Validator
from .word import KeyInfo, KeyInfoJson, Word


class EmptyPuzzleError(Exception):
    """Raised when attempting to access puzzle data before generation.

    This exception is raised when methods that require a completed puzzle
    are called before the puzzle has been generated or when the puzzle
    has no successfully placed words.

    Common scenarios:
    - Calling show(), save(), or json property before adding words
    - Generator fails to place any words due to constraints
    - Puzzle is reset without regeneration

    Example:
        >>> game = Game()  # No words added
        >>> game.show()   # Raises EmptyPuzzleError
    """

    def __init__(self, message="Try adding words using the `add_words()` method."):
        self.message = message
        super().__init__(self.message)


class MissingGeneratorError(Exception):
    """Raised when puzzle generation is attempted without a generator.

    The Game class requires a Generator instance to place words and fill
    the puzzle grid. This error occurs when generate() is called but no
    generator was provided in the constructor or set via the property.

    Example:
        >>> game = Game(words="cat dog", generator=None)
        >>> game.generate()  # Raises MissingGeneratorError
    """

    def __init__(self, message="Generator required for puzzle generation."):
        self.message = message
        super().__init__(self.message)


class MissingFormatterError(Exception):
    """Raised when puzzle output is attempted without a formatter.

    The Game class requires a Formatter instance to display or save
    puzzles. This error occurs when show() or save() methods are called
    but no formatter was provided in the constructor or set via the property.

    Example:
        >>> game = Game(words="cat dog", formatter=None)
        >>> game.show()  # Raises MissingFormatterError
    """

    def __init__(self, message="Formatter required for outputting the puzzle."):
        self.message = message
        super().__init__(self.message)


class PuzzleSizeError(ValueError):
    """Raised when an invalid puzzle size is specified.

    Puzzle sizes must be integers within the valid range defined by
    MIN_PUZZLE_SIZE and MAX_PUZZLE_SIZE constants. Also raised when
    the specified size is smaller than the longest word to be placed.

    Example:
        >>> game = Game(size=2)    # Too small - raises PuzzleSizeError
        >>> game = Game(size=100)  # Too large - raises PuzzleSizeError
        >>> game = Game(words="verylongword", size=5)  # Raises PuzzleSizeError
    """

    pass


class EmptyWordlistError(Exception):
    """Raised when puzzle generation is attempted with no words.

    The Game class requires at least one word to generate a puzzle.
    This error occurs when generate() is called but the word list
    is empty or was never populated.

    Example:
        >>> game = Game()  # No words specified
        >>> game.generate()  # Raises EmptyWordlistError
    """

    pass


class NoValidWordsError(Exception):
    """Raised when no words pass validation or can be placed.

    This error occurs when all provided words are either filtered out
    by validators or cannot be placed in the puzzle due to size or
    geometric constraints. Common causes include overly restrictive
    validators, words too long for the puzzle, or conflicting masks.

    Example:
        >>> game = Game(words="superlongwordthatcannotfit", size=5)
        >>> # Raises NoValidWordsError during generation
    """

    pass


class MissingWordError(Exception):
    """Raised when require_all_words=True but some words cannot be placed.

    When the Game is configured to require all words to be successfully
    placed, this error is raised if the generator cannot fit every word
    in the puzzle due to space constraints or conflicts.

    Example:
        >>> game = Game(words="cat dog bird", size=5, require_all_words=True)
        >>> # May raise MissingWordError if not enough space
    """

    pass


# Type Aliases for Game Components

Puzzle: TypeAlias = list[list[str]]
"""2D grid representing the puzzle letter matrix.

A puzzle is stored as a list of rows, where each row is a list of single
characters. This structure supports both the main puzzle grid and mask
overlays. Characters can be letters (A-Z) or special mask markers.

Example:
    [["A", "B", "C"], ["D", "E", "F"], ["G", "H", "I"]]
"""

DirectionSet: TypeAlias = set[Direction]
"""Set of allowed word placement directions for puzzle generation.

Contains Direction enum values that define which orientations words can
be placed in the puzzle (horizontal, vertical, diagonal, etc.). Used to
control puzzle difficulty by limiting available directions.

Example:
    {Direction.E, Direction.S, Direction.SE}  # Right, Down, Diagonal
"""

Key: TypeAlias = dict[str, KeyInfo]
"""Answer key mapping word text to placement details.

Dictionary where keys are word strings and values are KeyInfo objects
containing position, direction, and coordinate information for placed words.
Provides the solution data needed to highlight words in the puzzle.

Example:
    {"CAT": KeyInfo(start=(1,1), direction=Direction.E, length=3)}
"""

KeyJson: TypeAlias = dict[str, KeyInfoJson]
"""JSON-serializable version of the answer key.

Similar to Key but with JSON-compatible value types instead of KeyInfo
objects. Used for exporting puzzle solutions in JSON format.

Example:
    {"CAT": {"start": [1,1], "direction": "E", "length": 3}}
"""

WordSet: TypeAlias = OrderedSet[Word]
"""Ordered collection of Word objects for puzzle generation.

OrderedSet maintains word insertion order while preventing duplicates.
This ensures consistent puzzle generation and allows users to control
word priority by insertion order.

Example:
    OrderedSet([Word("CAT"), Word("DOG"), Word("BIRD")])
"""


class Game:
    """Core word search puzzle game engine and orchestrator.

    The Game class serves as the main interface for creating, managing, and
    manipulating word search puzzles. It coordinates between generators, formatters,
    validators, and masks to create complete puzzle experiences.

    Key Features:
        - Automatic puzzle generation with configurable algorithms
        - Multiple output formats (PDF, text, JSON, etc.)
        - Geometric masking for custom puzzle shapes
        - Word validation and filtering
        - Direction control for difficulty adjustment
        - Size optimization based on word content

    Args:
        words: Words to include in the puzzle. Can be a space/comma-separated
            string or a WordSet collection.
        level: Difficulty level (int 1-4) or custom direction specification.
            Higher levels allow more directions (diagonal, backwards, etc.).
        size: Puzzle grid size in characters. Auto-calculated if not specified.
        require_all_words: If True, raises error if any words cannot be placed.
        generator: Word placement algorithm. Uses DEFAULT_GENERATOR if None.
        formatter: Output handler for display/export. Uses DEFAULT_FORMATTER if None.
        validators: Collection of word validation rules.

    Raises:
        TypeError: If size is not an integer.
        ValueError: If size is outside valid range or level is invalid.
        PuzzleSizeError: If specified size is too small for the longest word.

    Examples:
        Basic puzzle creation:

        >>> game = Game(words="cat dog bird mouse", level=2, size=15)
        >>> game.show()  # Display the puzzle
        >>> game.save("puzzle.pdf")  # Export to PDF

        Advanced configuration:

        >>> from word_search_generator.core import Generator, Formatter
        >>> game = Game(
        ...     words="python programming code",
        ...     level="E,S,SE,SW",  # Custom directions
        ...     require_all_words=True,
        ...     generator=MyCustomGenerator(),
        ...     formatter=MyCustomFormatter()
        ... )

        Working with masks:

        >>> from word_search_generator.mask import CircleMask
        >>> game = Game(words="circle round sphere", size=20)
        >>> game.apply_mask(CircleMask(10))  # Circular puzzle shape
        >>> game.show()

        JSON export:

        >>> game = Game(words="export json data")
        >>> puzzle_data = game.json  # Get JSON representation
        >>> print(game.key)  # View answer key
    """

    # Puzzle Size Constraints
    MIN_PUZZLE_SIZE = 5
    """Minimum allowed puzzle grid size in characters.

    Puzzles smaller than this size cannot accommodate most words and provide
    insufficient challenge. This constraint ensures puzzles have adequate space
    for word placement and random filler characters.
    """

    MAX_PUZZLE_SIZE = 50
    """Maximum allowed puzzle grid size in characters.

    Large puzzles become difficult to solve and consume excessive computational
    resources during generation. This limit balances puzzle complexity with
    practical performance constraints.
    """

    MIN_PUZZLE_WORDS = 1
    """Minimum number of words required for puzzle generation.

    At least one word is needed to create a meaningful word search puzzle.
    This constraint prevents empty or invalid puzzle creation attempts.
    """

    MAX_PUZZLE_WORDS = 100
    """Maximum number of words allowed in a single puzzle.

    Too many words can make puzzles unsolvable and may cause generation
    failures due to space constraints. This limit ensures reasonable
    puzzle complexity and generation performance.
    """

    MAX_FIT_TRIES = 1000
    """Maximum attempts for placing words during generation.

    This limit prevents infinite loops when word placement is impossible
    due to geometric constraints, conflicting words, or insufficient space.
    Generator algorithms use this value to determine when to give up on
    placing remaining words.
    """

    # Default Component Configuration
    DEFAULT_GENERATOR: Generator | None = None
    """Default generator instance used when none is specified.

    If None, users must provide a generator or set this class attribute
    before creating Game instances. Allows global configuration of the
    default word placement algorithm.
    """

    DEFAULT_FORMATTER: Formatter | None = None
    """Default formatter instance used when none is specified.

    If None, users must provide a formatter or set this class attribute
    before using display/export methods. Allows global configuration of
    the default output formatting.
    """

    DEFAULT_VALIDATORS: Iterable[Validator] = []
    """Default word validation rules applied during generation.

    Empty list means no validation by default. Can be set to a collection
    of Validator instances to apply global word filtering rules across
    all Game instances.
    """

    # Mask Character Constants
    ACTIVE = "*"
    """Character marking active/available grid cells in puzzle masks.

    Cells marked with this character can contain words and filler letters.
    Used internally by the masking system to define the active puzzle area
    when geometric constraints are applied.
    """

    INACTIVE = "#"
    """Character marking inactive/blocked grid cells in puzzle masks.

    Cells marked with this character are excluded from puzzle generation
    and display. Used internally by the masking system to create custom
    puzzle shapes and geometric constraints.
    """

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
        self._words: WordSet = OrderedSet()
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
        return self._words.copy()

    @property
    def placed_words(self) -> WordSet:
        """Words of any type currently placed in the puzzle."""
        return OrderedSet(word for word in self.words if word.placed)

    @property
    def unplaced_words(self) -> WordSet:
        """Words of any type not currently placed in the puzzle."""
        return OrderedSet(word for word in self.words if not word.placed)

    @property
    def puzzle(self) -> Puzzle:
        """The current puzzle state."""
        return self._puzzle

    @property
    def solution(self) -> None:
        """Display the puzzle solution with words highlighted.

        This property has the side effect of printing the puzzle solution
        directly to stdout using the configured formatter. Unlike other
        properties, it does not return a value but triggers display output.

        Raises:
            EmptyPuzzleError: If puzzle is not generated or has no placed words.
            MissingFormatterError: If no formatter is configured.

        Note:
            This property modifies program state by printing output. Consider
            using the show() method directly for more explicit behavior.
        """
        self.show(solution=True)

    @property
    def mask(self) -> Puzzle:
        """The current puzzle mask defining active/inactive grid areas.

        The mask is a 2D grid where each cell contains either ACTIVE ('*')
        or INACTIVE ('#') characters. ACTIVE cells can contain words and
        filler characters, while INACTIVE cells are excluded from puzzle
        generation and display.

        Returns:
            2D list representing the mask state, with ACTIVE/INACTIVE markers.

        Note:
            The mask dimensions always match the puzzle size. If no explicit
            masks have been applied, all cells default to ACTIVE.
        """
        return self._mask

    @property
    def masks(self) -> list[Mask]:
        """List of all mask objects applied to this puzzle.

        Contains all Mask instances that have been applied using apply_mask()
        or apply_masks(). Each mask defines a geometric shape or pattern that
        constrains where words can be placed in the puzzle grid.

        Returns:
            List of Mask objects currently applied to the puzzle. Empty list
            indicates no masks are active (full rectangular grid).

        See Also:
            apply_mask(): Apply a single mask to the puzzle
            apply_masks(): Apply multiple masks to the puzzle
            remove_masks(): Clear all applied masks
        """
        return self._masks

    @property
    def masked(self) -> bool:
        """Whether any masks are currently applied to the puzzle.

        Returns True if one or more mask objects have been applied using
        apply_mask() or apply_masks(), False if the puzzle uses the default
        rectangular grid without geometric constraints.

        Returns:
            True if masks are active, False for standard rectangular puzzles.

        Note:
            This is equivalent to checking if the masks list is non-empty.
        """
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
        """Answer key mapping word text to placement information.

        Creates a dictionary where each key is a placed word's text and each
        value contains the word's position, direction, and coordinate details.
        Coordinates are 1-based and reference the entire puzzle grid, not just
        the active masked area.

        Returns:
            Dictionary mapping word text to KeyInfo objects containing:
            - start_position: (row, col) where word begins (1-based)
            - direction: Direction enum indicating word orientation
            - length: Number of characters in the word

        Note:
            Only includes words that were successfully placed in the puzzle.
            Unplaced words are excluded from the answer key.
        """
        return {word.text: word.key_info for word in self.placed_words}

    @property
    def json(self) -> str:
        """JSON representation of the puzzle and placed words.

        Creates a JSON string containing the cropped puzzle grid and a list
        of all successfully placed word texts. The puzzle grid only includes
        the active area defined by the bounding box, excluding empty borders.

        Returns:
            JSON string with two fields:
            - "puzzle": 2D array of the cropped puzzle grid
            - "words": List of placed word texts (strings)

        Raises:
            EmptyPuzzleError: If puzzle is not generated or has no placed words.

        Example:
            >>> game.json
            '{"puzzle": [["A","B","C"], ["D","E","F"]], "words": ["ABC", "DEF"]}'
        """
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

    def save(
        self,
        path: str | Path,
        format: ExportFormat = ExportFormat.PDF,
        *args,
        **kwargs,
    ) -> Path:
        """Save the current puzzle to a file.

        Args:
            path: File save path.
            format: Export format. Defaults to ExportFormat.PDF.

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
        return self.formatter.save(self, path, format, *args, **kwargs)

    # *************************************************************** #
    # ******************** PROCESSING/GENERATION ******************** #
    # *************************************************************** #

    @staticmethod
    def _build_puzzle(size: int, char: str) -> Puzzle:
        """Build an empty nested list/puzzle grid."""
        return [[char] * size for _ in range(size)]

    def generate(self, reset_size: bool = False) -> None:
        """Generate the complete puzzle grid with word placement and filler.

        This is the core method that orchestrates the entire puzzle creation
        process. It coordinates word placement, mask application, and filler
        character generation to produce a complete, solvable puzzle.

        The generation process follows these steps:
        1. Validates that a generator is available
        2. Ensures at least one word exists for placement
        3. Calculates optimal puzzle size (if needed)
        4. Validates size constraints against word lengths
        5. Clears any previous word placements
        6. Initializes or updates the mask grid
        7. Delegates to the generator for word placement and filling
        8. Validates generation results and requirements

        Args:
            reset_size: If True, recalculates the optimal puzzle size based on
                current words and difficulty level before generation. Useful when
                words have been added/removed or level changed. Defaults to False.

        Raises:
            MissingGeneratorError: No generator instance is configured. Set via
                constructor or the generator property.
            EmptyWordlistError: The word list is empty. Add words using add_words()
                or provide them in the constructor.
            PuzzleSizeError: The current size is invalid or smaller than the
                longest word that needs to be placed.
            NoValidWordsError: All words were filtered out by validators or none
                could be placed due to constraints. Check validators and puzzle size.
            MissingWordError: Some words couldn't be placed when require_all_words=True.
                Consider increasing puzzle size or reducing difficulty.

        Example:
            >>> game = Game(words="cat dog bird")
            >>> game.generate()  # Creates puzzle with current settings
            >>> game.add_words("mouse")
            >>> game.generate(reset_size=True)  # Recalculates size for new words
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
        word_set: WordSet = OrderedSet()
        while word_list and len(word_set) <= self.MAX_PUZZLE_WORDS:
            word = word_list.pop(0)
            if word:
                word_set.add(Word(word, secret=secret))
        return word_set

    @staticmethod
    def _validate_direction_iterable(
        d: Iterable[str | tuple[int, int] | Direction],
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
            elif isinstance(direction, str):
                try:
                    o.add(Direction[direction.upper().strip()])
                except KeyError as e:
                    e.add_note(f"'{direction}' is not a valid direction.")
                    raise ValueError() from e
        return o

    def validate_level(self, d) -> DirectionSet:
        """Convert level specification to a validated set of Direction enums.

        This method provides flexible input handling for difficulty levels and
        custom direction specifications. It supports numeric difficulty levels,
        comma-separated direction strings, and collections of direction objects.

        Numeric levels correspond to predefined difficulty settings:
        - Level 1: Horizontal and vertical only (easiest)
        - Level 2: Adds basic diagonals
        - Level 3: Includes reverse directions
        - Level 4: All directions including complex diagonals (hardest)

        Args:
            d: Direction specification. Can be:
                - int: Predefined difficulty level (1-4)
                - str: Comma-separated direction names ("E,S,SE")
                - Iterable: Collection of Direction objects, strings, or tuples

        Returns:
            Set of validated Direction enum values for word placement.

        Raises:
            ValueError: If numeric level is invalid, direction name is unknown,
                or empty iterable is provided.
            TypeError: If input type is not supported (not str, int, or Iterable).
            KeyError: If direction string doesn't match any Direction enum name.

        Examples:
            >>> game.validate_level(2)  # Returns predefined level 2 directions
            >>> game.validate_level("E,S,SE")  # Custom direction set
            >>> game.validate_level([Direction.E, Direction.S])  # Direction objects
            >>> game.validate_level([(1,0), (0,1)])  # Tuple coordinates
        """
        if isinstance(d, int):  # traditional numeric level
            try:
                return LEVEL_DIRS[d]
            except KeyError as e:
                e.add_note(
                    f"{d} is not a valid difficulty number"
                    + f"[{', '.join([str(i) for i in LEVEL_DIRS])}]"
                )
                raise ValueError() from e
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
        """Apply a geometric mask to constrain puzzle shape and word placement.

        Masks define custom shapes for puzzles by marking grid cells as active
        or inactive. This enables creation of themed puzzles (circles, stars, etc.)
        or puzzles that fit specific layouts. The mask is combined with the current
        puzzle state using the mask's specified method.

        Mask Application Methods:
        - Method 1 (Intersection): Only cells active in both mask and current state
        - Method 2 (Union): Cells active in either mask or current state
        - Method 3 (Exclusion): Deactivate cells marked as active in the mask

        The mask is automatically resized to match the puzzle dimensions if needed.
        After application, the puzzle is regenerated to reflect the new constraints.

        Args:
            mask: Mask object defining the geometric constraints. Must be a Mask
                or CompoundMask instance with appropriate dimensions and method.

        Raises:
            EmptyPuzzleError: If no puzzle has been generated yet. Call generate()
                or ensure words are added first.
            TypeError: If mask is not a Mask or CompoundMask instance.

        Example:
            >>> from word_search_generator.mask import CircleMask, StarMask
            >>> game = Game(words="circle round sphere")
            >>> game.apply_mask(CircleMask(radius=8))  # Circular puzzle
            >>>
            >>> # Apply multiple masks
            >>> game.apply_mask(StarMask(points=5, size=10))
            >>>
            >>> # View current mask state
            >>> game.show_mask()

        Note:
            The mask is added to the masks collection and can be removed later
            using remove_masks(). Applying multiple masks creates compound effects.
        """
        if not self.puzzle:
            raise EmptyPuzzleError()
        if not isinstance(mask, Mask | CompoundMask):
            raise TypeError("Please provide a Mask object.")
        if mask.puzzle_size != self.size:
            mask.generate(self.size)
        for y in range(self.size):
            for x in range(self.size):
                self.mask[y][x] = self.mask[y][x]
                mask.mask[y][x] = mask.mask[y][x]
                match mask.method:
                    case 1:
                        self.mask[y][x] = (
                            self.ACTIVE
                            if mask.mask[y][x] == self.mask[y][x] == self.ACTIVE
                            else self.INACTIVE
                        )
                    case 2:
                        if mask.mask[y][x] == self.ACTIVE:
                            self.mask[y][x] = self.ACTIVE
                    case 3:
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
        self._mask = list(map(list, zip(*self.mask, strict=False)))
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
