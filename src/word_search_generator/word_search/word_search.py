"""Primary WordSearch puzzle class.

This module exposes ``WordSearch``, the user-facing entry point for creating,
displaying, and saving word-search puzzles.  It wires together the default
generator, formatter, and validators defined elsewhere in the package and adds
word-search-specific features such as secret words and independent secret-word
direction sets.
"""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from ordered_set import OrderedSet

from ..core.formatter import ExportFormat, Formatter
from ..core.game import (
    DirectionSet,
    EmptyPuzzleError,
    EmptyWordlistError,
    Game,
    MissingGeneratorError,
    MissingWordError,
    PuzzleSizeError,
    WordSet,
)
from ..core.generator import Generator
from ..core.validator import (
    NoPalindromes,
    NoPunctuation,
    NoSingleLetterWords,
    NoSubwords,
    Validator,
)
from ..utils import get_random_words
from ._formatter import WordSearchFormatter
from ._generator import WordSearchGenerator


class WordSearch(Game):
    """User-facing word-search puzzle.

    Extends the base :class:`~word_search_generator.core.game.Game` with
    word-search-specific features: secret words that are hidden from the
    word list, an independent direction set for those secret words, and
    sensible defaults for the generator, formatter, and word validators.

    Class Attributes:
        MIN_PUZZLE_SIZE: Smallest allowed grid side length.
        MAX_PUZZLE_SIZE: Largest allowed grid side length.
        MIN_PUZZLE_WORDS: Minimum number of words accepted.
        MAX_PUZZLE_WORDS: Maximum number of words the generator will place.
        MAX_FIT_TRIES: Per-word retry limit passed to the generator.
        DEFAULT_GENERATOR: ``WordSearchGenerator`` instance used when none is
            provided.
        DEFAULT_FORMATTER: ``WordSearchFormatter`` instance used when none is
            provided.
        DEFAULT_VALIDATORS: List of built-in validators (no palindromes, no
            punctuation, no single-letter words, no sub-words).
    """

    MIN_PUZZLE_SIZE: ClassVar[int] = 5
    MAX_PUZZLE_SIZE: ClassVar[int] = 50
    MIN_PUZZLE_WORDS: ClassVar[int] = 1
    MAX_PUZZLE_WORDS: ClassVar[int] = 100
    MAX_FIT_TRIES: ClassVar[int] = 1000

    DEFAULT_GENERATOR: ClassVar[Generator | None] = WordSearchGenerator()
    DEFAULT_FORMATTER: ClassVar[Formatter | None] = WordSearchFormatter()
    DEFAULT_VALIDATORS: ClassVar[Iterable[Validator]] = [
        NoPalindromes(),
        NoPunctuation(),
        NoSingleLetterWords(),
        NoSubwords(),
    ]

    def __init__(
        self,
        words: str | None = None,
        level: int | str | None = None,
        size: int | None = None,
        secret_words: str | None = None,
        secret_level: int | str | None = None,
        *,
        require_all_words: bool = False,
        generator: Generator | None = None,
        formatter: Formatter | None = None,
        validators: Iterable[Validator] | None = DEFAULT_VALIDATORS,
    ) -> None:
        """Create a new word-search puzzle.

        If ``words`` (or ``secret_words``) is provided the puzzle is
        generated immediately.  Omit both to create an empty puzzle and
        populate it later with :meth:`add_words`.

        Args:
            words: Words separated by spaces, commas, or newlines.  Excess
                words beyond ``MAX_PUZZLE_WORDS`` are silently dropped.
                Defaults to None.
            level: Preset difficulty (1–3) or a comma-separated string of
                cardinal directions (e.g. ``"N,S,E,W"``).  Controls which
                directions hidden words may travel.  Defaults to 2.
            size: Square grid side length.  Must fall within
                ``[MIN_PUZZLE_SIZE, MAX_PUZZLE_SIZE]``.  Calculated
                automatically when None.  Defaults to None.
            secret_words: Same format as ``words``.  These words are placed
                in the grid but omitted from the printed word list.
                Defaults to None.
            secret_level: Direction constraint for secret words, using the
                same format as ``level``.  Defaults to the value of
                ``level`` (or 2 if that is also None).
            require_all_words: When True, :meth:`generate` raises
                :exc:`~word_search_generator.core.game.MissingWordError` if
                any hidden word could not be placed.  Secret words are
                excluded from this check.  Defaults to False.
            generator: Custom :class:`~word_search_generator.core.generator.Generator`.
                Defaults to ``DEFAULT_GENERATOR``.
            formatter: Custom :class:`~word_search_generator.core.formatter.Formatter`.
                Defaults to ``DEFAULT_FORMATTER``.
            validators: Validators applied to each word before placement.
                Pass an empty iterable to disable all validation.
                Defaults to ``DEFAULT_VALIDATORS``.
        """
        # determine valid word directions
        self._secret_directions: DirectionSet = (
            self.validate_level(secret_level)
            if secret_level
            else (self.validate_level(level) if level else self.validate_level(2))
        )

        # setup words
        word_set = WordSet()
        if words:
            word_set.update(self._process_input(words))
        if secret_words:
            word_set.update(self._process_input(secret_words, secret=True))

        super().__init__(
            words=word_set,
            level=level,
            size=size,
            require_all_words=require_all_words,
            generator=generator,
            formatter=formatter,
            validators=validators,
        )

    # **************************************************** #
    # ******************** PROPERTIES ******************** #
    # **************************************************** #

    @property
    def hidden_words(self) -> WordSet:
        """Words of type "hidden"."""
        return WordSet(word for word in self.words if not word.secret)

    @property
    def placed_hidden_words(self) -> WordSet:
        """Words of type "hidden" currently placed in the puzzle."""
        return WordSet(word for word in self.placed_words if not word.secret)

    @property
    def unplaced_hidden_words(self) -> WordSet:
        """Words of type "hidden" not currently placed in the puzzle."""
        return OrderedSet(self.hidden_words - self.placed_hidden_words)

    @property
    def secret_words(self) -> WordSet:
        """Words of type "secret"."""
        return WordSet(word for word in self.words if word.secret)

    @property
    def placed_secret_words(self) -> WordSet:
        """Words of type "secret" currently placed in the puzzle."""
        return WordSet(word for word in self.placed_words if word.secret)

    @property
    def unplaced_secret_words(self) -> WordSet:
        """Words of type "secret" not currently placed in the puzzle."""
        return OrderedSet(self.secret_words - self.placed_secret_words)

    @property
    def json(self) -> str:
        """The current puzzle, words, and answer key in JSON."""
        if not self.puzzle or not self.placed_words:
            raise EmptyPuzzleError()
        return json.dumps(
            {
                "puzzle": self.cropped_puzzle,
                "words": [word.text for word in self.placed_words],
                "key": {
                    word.text: word.key_info_json for word in self.words if word.placed
                },
            }
        )

    # ********************************************************* #
    # ******************** GETTERS/SETTERS ******************** #
    # ********************************************************* #

    @property
    def secret_directions(self) -> DirectionSet:
        """Valid directions for secret puzzle words."""
        return self._secret_directions

    @secret_directions.setter
    def secret_directions(self, value: int | str | Iterable[str]) -> None:
        """Set the allowed directions for secret words and regenerate.

        Args:
            value: A preset difficulty level (int), a comma-separated string
                of cardinal directions (e.g. ``"N,S,E,W"``), or an iterable
                of valid :class:`~word_search_generator.core.word.Direction`
                values.  The puzzle is regenerated automatically after the
                change.
        """
        self._secret_directions = self.validate_level(value)
        self.generate()

    # ************************************************* #
    # ******************** METHODS ******************** #
    # ************************************************* #

    def show(
        self,
        solution: bool = False,
        hide_fillers: bool = False,
        lowercase: bool = False,
        hide_key: bool = False,
        reversed_letters: bool = False,
        sort_word_list: bool = True,
    ) -> None:
        """Display the current puzzle in the console.

        Prints a formatted representation of the word search puzzle with optional
        styling and formatting options. This method displays the puzzle grid, word list,
        and answer key based on the provided parameters.

        Args:
            solution: Highlight the puzzle solution with colored words. When True,
                placed words are shown with color highlighting. Defaults to False.
            hide_fillers: Hide filler letters (show only placed words). When True,
                only letters that are part of actual words are displayed, with filler
                characters replaced by spaces. Defaults to False.
            lowercase: Convert all letters to lowercase. When True, all puzzle letters
                and words in the list are displayed in lowercase. Defaults to False.
            hide_key: Hide the answer key from the output. When True, the answer key
                showing word positions and directions is not displayed at the bottom
                of the puzzle. Defaults to False.
            reversed_letters: Show reversed letter positions in the answer key.
                Affects how word coordinates are displayed in the key.
                Defaults to False.
            sort_word_list: Sort the word list alphabetically. When True, words are
                displayed in alphabetical order. When False, words appear in the order
                they were added to the puzzle. Defaults to True.

        Raises:
            EmptyPuzzleError: If puzzle is not generated or has no placed words.
            MissingFormatterError: If no formatter is configured.

        Examples:
            Display a basic puzzle:

            >>> ws = WordSearch("cat dog bird")
            >>> ws.show()

            Display with solution highlighted:

            >>> ws.show(solution=True)

            Display only the placed words (no fillers):

            >>> ws.show(hide_fillers=True)

            Display in lowercase without answer key:

            >>> ws.show(lowercase=True, hide_key=True)

            Display with words in original order:

            >>> ws.show(sort_word_list=False)
        """
        return super().show(
            solution=solution,
            hide_fillers=hide_fillers,
            lowercase=lowercase,
            hide_key=hide_key,
            reversed_letters=reversed_letters,
            sort_word_list=sort_word_list,
        )

    def save(
        self,
        path: str | Path,
        format: ExportFormat = ExportFormat.PDF,
        *args,
        **kwargs,
    ) -> Path:
        """Save the current puzzle to a file.

        This method supports additional formatting options through keyword arguments
        that control how the puzzle is displayed and saved.

        Args:
            path: File save path.
            format: Export format. Defaults to ExportFormat.PDF.
            **kwargs: Additional formatting options:
                solution (bool): Show solution with word highlighted.
                    Defaults to False.
                lowercase (bool): Convert all letters to lowercase. Defaults to False.
                hide_key (bool): Hide the answer key from the output. Defaults to False.
                sort_word_list (bool): Sort the word list alphabetically. If False,
                    words appear in the order they were added. Defaults to True.

        Raises:
            EmptyPuzzleError: Puzzle not yet generated or puzzle has no placed words.
            MissingFormatterError: No puzzle formatter set.

        Returns:
            Final save path of the file.

        Examples:
            Save a basic puzzle:

            >>> ws = WordSearch("cat dog bird")
            >>> ws.save("puzzle.pdf")

            Save with solution highlighted:

            >>> ws.save("solution.pdf", solution=True)

            Save as CSV with lowercase letters and no answer key:

            >>> ws.save(
            ...     "puzzle.csv",
            ...     format=ExportFormat.CSV,
            ...     lowercase=True,
            ...     hide_key=True,
            ... )

            Save with words in original order (unsorted):

            >>> ws.save("puzzle.pdf", sort_word_list=False)
        """
        solution = kwargs.get("solution", False)
        lowercase = kwargs.get("lowercase", False)
        hide_key = kwargs.get("hide_key", False)
        sort_word_list = kwargs.get("sort_word_list", True)
        return super().save(
            path=path,
            format=format,
            solution=solution,
            lowercase=lowercase,
            hide_key=hide_key,
            sort_word_list=sort_word_list,
        )

    # *************************************************************** #
    # ******************** PROCESSING/GENERATION ******************** #
    # *************************************************************** #

    def random_words(
        self,
        count: int,
        word_list: list[str] | None = None,
        action: str = "REPLACE",
        secret: bool = False,
        reset_size: bool = False,
    ) -> None:
        """Populate the puzzle with randomly-sampled words.

        Words are drawn from ``word_list`` when provided; otherwise they
        come from the package's built-in dictionary.

        Args:
            count: Number of random words to sample.  Must be in
                ``[MIN_PUZZLE_WORDS, MAX_PUZZLE_WORDS]``.
            word_list: Source pool to sample from.  When None the
                package's built-in word list is used.  Defaults to None.
            action: ``"ADD"`` appends the new words to the existing word
                list; ``"REPLACE"`` swaps them in.  Case-insensitive.
                Defaults to ``"REPLACE"``.
            secret: When True the sampled words are marked as secret
                (hidden from the printed word list).  Defaults to False.
            reset_size: When True the puzzle grid is resized to fit the
                updated word list before regeneration.  Defaults to False.

        Raises:
            TypeError: If ``count`` is not an integer or ``action`` is not
                a string.
            ValueError: If ``count`` is outside
                ``[MIN_PUZZLE_WORDS, MAX_PUZZLE_WORDS]`` or ``action`` is
                not one of ``"ADD"`` / ``"REPLACE"``.
        """
        if not isinstance(count, int):
            raise TypeError(f"Count must be an integer, got {type(count).__name__}.")
        if not self.MIN_PUZZLE_WORDS <= count <= self.MAX_PUZZLE_WORDS:
            raise ValueError(
                f"Random word count must be between {self.MIN_PUZZLE_WORDS} and "
                f"{self.MAX_PUZZLE_WORDS} (inclusive), got {count}."
            )
        if not isinstance(action, str):
            raise TypeError(f"Action must be a string, got {type(action).__name__}.")
        if action.upper() not in ["ADD", "REPLACE"]:
            valid_actions = "ADD, REPLACE"
            raise ValueError(f"Action must be one of: {valid_actions}. Got '{action}'.")
        if action.upper() == "ADD":
            self.add_words(
                get_random_words(count, word_list=word_list),
                secret=secret,
                reset_size=reset_size,
            )
        else:
            self.replace_words(
                get_random_words(count, word_list=word_list),
                secret=secret,
                reset_size=reset_size,
            )

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
            raise EmptyWordlistError(
                "Cannot generate puzzle: no words have been added. "
                "Use add_words() to add words to the puzzle."
            )
        if not self.size or reset_size:
            self.size = self._calc_puzzle_size(self._words, self._directions)
        min_word_length = (
            min([len(word.text) for word in self.words]) if self.words else self.size
        )
        if self.size and self.size < min_word_length:
            raise PuzzleSizeError(
                f"Puzzle size ({self.size}) is too small for the shortest word "
                f"({min_word_length} characters). Increase puzzle size to at "
                f"least {min_word_length} or reduce word length."
            )
        for word in self.words:
            word.remove_from_puzzle()
        if not self.mask or len(self.mask) != self.size:
            self._mask = self._build_puzzle(self.size, self.ACTIVE)
        self._puzzle = self.generator.generate(self)
        if self.require_all_words and self.unplaced_hidden_words:
            unplaced_texts = [w.text for w in list(self.unplaced_hidden_words)[:5]]
            unplaced_str = ", ".join(unplaced_texts)
            more_indicator = "..." if len(self.unplaced_hidden_words) > 5 else ""
            raise MissingWordError(
                f"Not all words could be placed in the puzzle. "
                f"{len(self.unplaced_hidden_words)} words were not placed: "
                f"{unplaced_str}{more_indicator}. Try increasing puzzle size "
                f"or disabling require_all_words."
            )

    # ******************************************************** #
    # ******************** DUNDER METHODS ******************** #
    # ******************************************************** #

    def __eq__(self, __o: object) -> bool:
        """Compare two WordSearch objects for equality.

        Two WordSearch objects are considered equal if they have the same words,
        directions, size, secret words, and secret directions. This comparison
        checks the configuration and word lists, not the generated puzzle state.

        Args:
            __o: Object to compare against.

        Returns:
            True if both objects are WordSearch instances with identical
            configuration (words, directions, size, secret words, and secret
            directions). False otherwise.

        Examples:
            >>> ws1 = WordSearch("cat dog", level=2, size=10)
            >>> ws2 = WordSearch("cat dog", level=2, size=10)
            >>> ws1 == ws2
            True

            >>> ws3 = WordSearch("cat dog", level=3, size=10)
            >>> ws1 == ws3
            False
        """
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

    def __repr__(self) -> str:
        """Return a detailed string representation of the WordSearch object.

        Creates a string that shows how to recreate the WordSearch instance,
        including all configuration parameters such as words, level, size,
        secret words, and additional settings.

        Returns:
            String representation in the format:
            WordSearch(words='...', level=..., size=..., secret_words='...',
                      secret_level=..., require_all_words=...)
        """
        return (
            f"{self.__class__.__name__}"
            + f"(words='{','.join([word.text for word in self.hidden_words])}', "
            + f"level={self.direction_set_repr}, "
            + f"size={self.size}, "
            + f"secret_words='{','.join([word.text for word in self.secret_words])}', "
            + f"secret_level={self.direction_set_repr}, "
            + f"require_all_words={self.require_all_words})"
        )
