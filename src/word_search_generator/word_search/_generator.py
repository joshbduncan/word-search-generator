from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING, TypeAlias

from ..core.generator import Generator, WordFitError, retry
from ..core.word import Direction, Word
from ..utils import in_bounds

if TYPE_CHECKING:  # pragma: no cover
    from ..core import GameType
    from ..core.game import Puzzle


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]


ALPHABET = list(string.ascii_uppercase)


class WordSearchGenerator(Generator):
    """Default generator for standard WordSearch puzzles."""

    def __init__(self) -> None:
        self.puzzle: Puzzle = []
        super().__init__()

    def generate(self, game: GameType) -> Puzzle:
        self.game = game
        self.puzzle = game._build_puzzle(game.size, "")
        self.fill_words()
        if any(word.placed for word in game.words):
            self.fill_blanks()
        return self.puzzle

    def no_duped_words(
        self, char: str, position: tuple[int, int], current_word: str | None = None
    ) -> bool:
        """Make sure that adding `char` at `position` will not create a
        duplicate of any word already placed in the puzzle."""
        placed_word_strings = []
        for word in self.game.words:
            if word.placed:
                if current_word and (
                    current_word in word.text or word.text in current_word
                ):
                    continue
                placed_word_strings.append(word.text)
        if not placed_word_strings:
            return True

        # calculate how large of a search radius to check
        radius = len(max(placed_word_strings, key=len))
        # track each directional fragment of characters
        fragments = self.capture_fragments(radius, position)
        # check to see if any duped words are now present
        before_ct = after_ct = 0
        for word_text in placed_word_strings:
            for before in fragments:
                # remove the current word
                # after = before.replace(current_word, "")
                after = before.replace("*", char)
                if word_text in before or word_text[::-1] in before:
                    before_ct += 1
                if word_text in after or word_text[::-1] in after:
                    after_ct += 1
        if before_ct == after_ct:
            return True
        return False

    def capture_fragments(self, radius: int, position: tuple[int, int]) -> list[str]:
        row, col = position
        fragments = []
        height = width = self.game.size

        # cardinal direction ranges to capture
        ranges = [
            (
                range(row - (radius - 1), row + radius),
                range(col - (radius - 1), col + radius),
            ),  # top-left to bottom-right
            (
                [row] * (radius * 2 - 1),
                range(col - (radius - 1), col + radius),
            ),  # left to right
            (
                range(row - (radius - 1), row + radius),
                [col] * (radius * 2 - 1),
            ),  # top to bottom
            (
                range(row + (radius - 1), row - radius, -1),
                range(col - (radius - 1), col + radius),
            ),  # bottom-left to top-right
        ]

        for row_range, col_range in ranges:
            fragment = ""
            for r, c in zip(row_range, col_range):
                if not in_bounds(c, r, width, height):
                    continue
                fragment += "*" if (r, c) == (row, col) else self.puzzle[r][c]
            fragments.append(fragment)
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
            if self.game.mask[row][col] == self.game.INACTIVE:
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
        directions = secret_directions = self.game.directions
        if hasattr(self.game, "secret_directions"):
            secret_directions = self.game.secret_directions
        for d in secret_directions if word.secret else directions:
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
        hidden_words = [word for word in self.game.words if not word.secret]
        secret_words = [word for word in self.game.words if word.secret]
        # try to place each secret word on the puzzle first before hidden words
        for word in hidden_words + secret_words:
            if self.game.validators and not word.validate(
                self.game.validators, placed_words
            ):
                continue
            fit = self.try_to_fit_word(word)
            if fit:
                placed_words.append(word.text)
            if len(placed_words) == self.game.MAX_PUZZLE_WORDS:
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
        if self.game.mask[row][col] == self.game.INACTIVE:
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
            if self.no_duped_words(char, (check_row, check_col), word.text):
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
                if (
                    self.puzzle[row][col] == ""
                    and self.game.mask[row][col] == self.game.ACTIVE
                ):
                    while True:
                        random_char = random.choice(ALPHABET)
                        if self.no_duped_words(random_char, (row, col)):
                            self.puzzle[row][col] = random_char
                            break
