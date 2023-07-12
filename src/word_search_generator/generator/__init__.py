from __future__ import annotations

import random
import string
from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Iterable, TypeAlias

from ..config import ACTIVE, INACTIVE, max_fit_tries, max_puzzle_words
from ..utils import build_puzzle, in_bounds
from ..word import Direction, Word, WordSet

if TYPE_CHECKING:  # pragma: no cover
    from .. import DirectionSet, Puzzle
    from ..validator import Validator


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]


ALPHABET = list(string.ascii_uppercase)


class WordFitError(Exception):
    pass


def retry(retries: int = max_fit_tries):
    """Custom retry decorator for retrying a function `retries` times.

    Args:
        retries (int, optional): Retry attempts. Defaults to max_fit_tries.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempt += 1
            return

        return wrapper

    return decorator


class Generator(ABC):
    """Base class for the puzzle generation algorithm.

    To implement your own `Generator`, subclass this class.

    Example:
        ```python
        class CoolGenerator(Generator):
            def validate(self,  *args, **kwargs) -> None:
                ...
        ```
    """

    def __init__(self) -> None:
        self.puzzle: Puzzle = []

    @abstractmethod
    def generate(
        self,
        size: int,
        mask: Puzzle,
        words: WordSet,
        directions: DirectionSet,
        secret_directions: DirectionSet,
        validators: Iterable[Validator],
        *args,
        **kwargs,
    ) -> Puzzle:
        """Generate a puzzle.

        Args:
            size (int): WordSearch size.
            mask (Puzzle): Current WordSearch mask.
            words (WordSet): WordSearch words to use for generation.
            directions (DirectionSet): Direction for hidden words.
            secret_directions (DirectionSet): Directions for secret words.
            validators (Iterable[Validator]): WordSearch word validators.

        Returns:
            Puzzle: Generated puzzle.
        """


class DefaultGenerator(Generator):
    """Default generator for standard WordSearch puzzles."""

    def generate(
        self,
        size: int,
        mask: Puzzle,
        words: WordSet,
        directions: DirectionSet,
        secret_directions: DirectionSet,
        validators: Iterable[Validator],
        *args,
        **kwargs,
    ) -> Puzzle:
        self.size = size
        self.mask = mask
        self.words = words
        self.directions = directions
        self.secret_directions = secret_directions
        self.validators = validators
        self.puzzle = build_puzzle(self.size, "")
        self.fill_words()
        if any(word.placed for word in self.words):
            self.fill_blanks()
        return self.puzzle

    def no_duped_words(self, char: str, position: tuple[int, int]) -> bool:
        """Make sure that adding `char` at `position` will not create a
        duplicate of any word already placed in the puzzle."""
        placed_word_strings = [word.text for word in self.words if word.placed]
        if not placed_word_strings:
            return True
        # calculate how large of a search radius to check
        radius = len(max(placed_word_strings, key=len))
        # track each directional fragment of characters
        fragments = self.capture_fragments(radius, position)
        # check to see if any duped words are now present
        before_ct = after_ct = 0
        for word in placed_word_strings:
            for before in fragments:
                after = before.replace("*", char)
                if word in before:
                    before_ct += 1
                if word[::-1] in before:
                    before_ct += 1
                if word in after:
                    after_ct += 1
                if word[::-1] in after:
                    after_ct += 1
        if before_ct == after_ct:
            return True
        return False

    def capture_fragments(self, radius: int, position: tuple[int, int]) -> list[str]:
        """Capture each directional fragment of characters from `position` outward
        to the `radius`.
        """
        row, col = position
        fragments = ["*"] * 4
        # while going out to match the calculated radius, grab each
        # neighboring character to add to the fragments
        for r in range(radius):
            dir_pairs = (
                ((-1, -1), (1, 1)),
                ((0, -1), (0, 1)),
                ((1, -1), (-1, 1)),
                ((-1, 0), (1, 0)),
            )
            for n, ((ly, lx), (ry, rx)) in enumerate(dir_pairs):
                # left and top traveling directions go on the left of the fragment
                n_row = row + (ly * (r + 1))
                n_col = col + (lx * (r + 1))
                if in_bounds(n_row, n_col, len(self.puzzle), len(self.puzzle)):
                    found = (
                        self.puzzle[n_row][n_col] if self.puzzle[n_row][n_col] else " "
                    )
                    fragments[n] = found + fragments[n]
                # right and bottom traveling directions go on the end of the fragment
                n_row = row + (ry * (r + 1))
                n_col = col + (rx * (r + 1))
                if in_bounds(n_row, n_col, len(self.puzzle), len(self.puzzle)):
                    found = (
                        self.puzzle[n_row][n_col] if self.puzzle[n_row][n_col] else " "
                    )
                    fragments[n] += found
        return fragments

    def test_a_fit(
        self,
        word: str,
        position: tuple[int, int],
        direction: Direction,
    ) -> list[tuple[int, int]]:
        """Test if word fits in the puzzle at the specified
        coordinates heading in the specified direction."""
        coordinates = []
        row, col = position
        # iterate over each letter in the word
        for char in word:
            # if coordinates are off of puzzle cancel fit test
            if not in_bounds(col, row, len(self.puzzle), len(self.puzzle)):
                return []
            # first check if the spot is inactive on the mask
            if self.mask[row][col] == INACTIVE:
                return []
            # if the current puzzle space is empty or if letters don't match
            if self.puzzle[row][col] != "" and self.puzzle[row][col] != char:
                return []
            coordinates.append((row, col))
            # adjust the coordinates for the next character
            row += direction.r_move
            col += direction.c_move
        return coordinates

    def find_a_fit(self, word: Word, position: tuple[int, int]) -> Fit:
        """Look for random place in the puzzle where `word` fits."""
        fits: Fits = []
        # check all directions for level
        for d in self.secret_directions if word.secret else self.directions:
            coords = self.test_a_fit(word.text, position, d)
            if coords:
                fits.append((Direction(d).name, coords))
        # if the word fits, pick a random fit for placement
        if not fits:
            raise WordFitError
        return random.choice(fits)

    def fill_words(self) -> None:
        """Fill puzzle with the supplied `words`.
        Some words will be skipped if they don't fit."""
        # try to place each word on the puzzle
        placed_words: list[str] = []
        hidden_words = [word for word in self.words if not word.secret]
        secret_words = [word for word in self.words if word.secret]
        # try to place each secret word on the puzzle first before hidden words
        for word in hidden_words + secret_words:
            if self.validators and not word.validate(self.validators, placed_words):
                continue
            fit = self.try_to_fit_word(word)
            if fit:
                placed_words.append(word.text)
            if len(placed_words) == max_puzzle_words:
                break

    @retry()
    def try_to_fit_word(self, word: Word) -> bool:
        """Try to fit `word` at randomized coordinates.
        @retry wrapper controls the number of attempts"""
        row = random.randint(0, len(self.puzzle) - 1)
        col = random.randint(0, len(self.puzzle) - 1)

        # no need to continue if random coordinate isn't available
        if self.puzzle[row][col] != "" and self.puzzle[row][col] != word.text[0]:
            raise WordFitError
        if self.mask[row][col] == INACTIVE:
            raise WordFitError

        # try and find a directional fit using the starting coordinates if not INACTIVE
        d, coords = self.find_a_fit(word, (row, col))

        # place word characters at fit coordinates
        previous_chars = []  # track previous to backtrack on WordFitError
        for i, char in enumerate(word.text):
            check_row = coords[i][0]
            check_col = coords[i][1]
            previous_chars.append(self.puzzle[check_row][check_col])

            # no need to check for dupes if characters are the same
            if char == self.puzzle[check_row][check_col]:
                continue
            # make sure placed character doesn't cause a duped word in the puzzle
            if self.no_duped_words(char, (check_row, check_col)):
                self.puzzle[check_row][check_col] = char
            else:
                # if a duped word was created put previous characters back in place
                for n, previous_char in enumerate(previous_chars):
                    self.puzzle[coords[n][0]][coords[n][1]] = previous_char
                raise WordFitError

        # update word placement info
        word.start_row = row
        word.start_column = col
        word.direction = Direction[d]
        word.coordinates = coords

        return word.placed

    def fill_blanks(self) -> None:
        """Fill empty puzzle spaces with random characters."""
        # iterate over the entire puzzle
        size = len(self.puzzle)
        for row in range(size):
            for col in range(size):
                # if the current spot is empty fill with random character
                if self.puzzle[row][col] == "" and self.mask[row][col] == ACTIVE:
                    while True:
                        random_char = random.choice(ALPHABET)
                        if self.no_duped_words(random_char, (row, col)):
                            self.puzzle[row][col] = random_char
                            break
