import json
from collections.abc import Iterable
from pathlib import Path

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
    """This class represents a WordSearch object."""

    MIN_PUZZLE_SIZE = 5
    MAX_PUZZLE_SIZE = 50
    MIN_PUZZLE_WORDS = 1
    MAX_PUZZLE_WORDS = 100
    MAX_FIT_TRIES = 1000

    DEFAULT_GENERATOR = WordSearchGenerator()
    DEFAULT_FORMATTER = WordSearchFormatter()
    DEFAULT_VALIDATORS = [
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
    ):
        """Initialize a game.

        Args:
            words: A string of words separated by spaces, commas, or new lines.
                Will be trimmed if more. Defaults to None.
            level: Difficulty level or potential word directions. Defaults to 2.
            size: Puzzle size. Defaults to None.
            secret_words: A string of words separated by spaces, commas, or new lines.
                Words will be 'secret' meaning they will not be included in the
                word list. Defaults to None.
            secret_level: Difficulty level or potential word directions for
                'secret' words. Defaults to None.
            require_all_words: Raises an error when `generator` cannot place all of
                the words.  Secret words are not included in this check.
            generator: Puzzle generator. Defaults to None.
            formatter: Game formatter. Defaults to None.
            validators: An iterable of validators that puzzle words will be checked
                against during puzzle generation. Provide an empty iterable to disable
                word validation. Defaults to `DEFAULT_VALIDATORS`.
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
    def secret_directions(self, value: int | str | Iterable[str]):
        """Possible directions for secret puzzle words.

        Args:
            val: Either a preset puzzle level (int), cardinal directions
                as a comma separated string, or an iterable of valid directions
                from the Direction object.
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
    ):
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
        solution: bool = False,
        lowercase: bool = False,
        hide_key: bool = False,
        sort_word_list: bool = True,
        *args,
        **kwargs,
    ) -> Path:
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
        """Add `count` randomly generated words to the puzzle.

        Args:
            count: Count of random words to add.
            word_list: _description_. Defaults to None.
            action: Should the random words be added ("ADD") to the current wordlist
                or should they replace ("REPLACE") the current wordlist.
                Defaults to "REPLACE".
            secret: Should the new words be secret. Defaults to False.
            reset_size: Reset the puzzle size based on the updated words.
                Defaults to False.

        Raises:
            TypeError: `count` must be an integer.
            ValueError: `count` must be greater than `self.MIN_PUZZLE_SIZE`
                and less than `self.MAX_PUZZLE_SIZE`.
            TypeError: `action` must be a string.
            ValueError: `action` must be one of ["ADD", "REPLACE"].
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
        return (
            f"{self.__class__.__name__}"
            + f"(words='{','.join([word.text for word in self.hidden_words])}', "
            + f"level={self.direction_set_repr}, "
            + f"size={self.size}, "
            + f"secret_words='{','.join([word.text for word in self.secret_words])}', "
            + f"secret_level={self.direction_set_repr}, "
            + f"require_all_words={self.require_all_words})"
        )
