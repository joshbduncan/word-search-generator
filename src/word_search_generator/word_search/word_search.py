import json
from collections.abc import Iterable
from pathlib import Path

from .. import utils
from ..core.formatter import Formatter
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
        word_set = set()
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
        return {word for word in self.words if not word.secret}

    @property
    def placed_hidden_words(self) -> WordSet:
        """Words of type "hidden" currently placed in the puzzle."""
        return {word for word in self.placed_words if not word.secret}

    @property
    def unplaced_hidden_words(self) -> WordSet:
        """Words of type "hidden" not currently placed in the puzzle."""
        return self.hidden_words - self.placed_hidden_words

    @property
    def secret_words(self) -> WordSet:
        """Words of type "secret"."""
        return {word for word in self.words if word.secret}

    @property
    def placed_secret_words(self) -> WordSet:
        """Words of type "secret" currently placed in the puzzle."""
        return {word for word in self.placed_words if word.secret}

    @property
    def unplaced_secret_words(self) -> WordSet:
        """Words of type "secret" not currently placed in the puzzle."""
        return self.secret_words - self.placed_secret_words

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
    ):
        return super().show(
            solution=solution,
            hide_fillers=hide_fillers,
            lowercase=lowercase,
            hide_key=hide_key,
            reversed_letters=reversed_letters,
        )

    def save(
        self,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
        lowercase: bool = False,
        hide_key: bool = False,
        *args,
        **kwargs,
    ) -> str:
        return super().save(
            path=path,
            format=format,
            solution=solution,
            lowercase=lowercase,
            hide_key=hide_key,
        )

    # *************************************************************** #
    # ******************** PROCESSING/GENERATION ******************** #
    # *************************************************************** #

    def random_words(
        self,
        count: int,
        action: str = "REPLACE",
        secret: bool = False,
        reset_size: bool = False,
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
                size based on the updated words. Defaults to False.

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be greater than `self.MIN_PUZZLE_SIZE` and
            less than `self.MAX_PUZZLE_SIZE`.
        """
        if not isinstance(count, int):
            raise TypeError("Size must be an integer.")
        if not Game.MIN_PUZZLE_WORDS <= count <= Game.MAX_PUZZLE_WORDS:
            raise ValueError(
                f"Requested random words must be >= {Game.MIN_PUZZLE_SIZE}"
                + f" and <= {Game.MAX_PUZZLE_WORDS}."
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
        if self.require_all_words and self.unplaced_hidden_words:
            raise MissingWordError("All words could not be placed in the puzzle.")

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
