"""Word-search puzzle generation algorithm.

This module provides ``WordSearchGenerator``, the default
:class:`~word_search_generator.core.generator.Generator` implementation.  It
places words into a square grid one at a time at random positions and
directions, rejects placements that would create duplicate words, and fills
every remaining active cell with a random letter from the configured
alphabet.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, TypeAlias

from ..core.game import Puzzle
from ..core.generator import Generator, WordFitError, retry
from ..core.word import Direction, Word
from ..utils import in_bounds

if TYPE_CHECKING:
    from ..core import Game
    from ..core.game import DirectionSet, Puzzle


Fit: TypeAlias = tuple[str, list[tuple[int, int]]]
Fits: TypeAlias = list[tuple[str, list[tuple[int, int]]]]


class WordSearchGenerator(Generator):
    """Default generator for standard WordSearch puzzles.

    Implements the core puzzle generation algorithm that:
    1. Places words in the grid according to direction constraints
    2. Handles both regular and secret words with different placement rules
    3. Fills remaining spaces with random characters to complete the puzzle
    4. Includes validation to prevent unintended word duplicates
    """

    def generate(self, game: Game) -> Puzzle:
        """Generate a completed puzzle grid for the given game.

        Initialises an empty grid, attempts to place every word via
        :meth:`fill_words`, then fills remaining active cells with random
        filler characters via :meth:`fill_blanks`.  The filler step is
        skipped entirely when no word was successfully placed (avoids an
        infinite loop on an empty grid).

        Args:
            game: The game instance that owns the word list, mask, and
                size information.

        Returns:
            The completed ``size × size`` puzzle grid.
        """
        self.game = game
        self.puzzle = game._build_puzzle(game.size, "")
        self.fill_words()
        if any(word.placed for word in game.words):
            self.fill_blanks()
        return self.puzzle

    def no_duped_words(
        self, char: str, position: tuple[int, int], current_word: str | None = None
    ) -> bool:
        """Check whether placing ``char`` at ``position`` keeps the grid dupe-free.

        Captures character fragments radiating outward from ``position``
        in all four axis-aligned and diagonal directions, substitutes the
        candidate character, and compares the before/after occurrence
        counts of every already-placed word (forward and reversed).  Words
        that are substrings of (or contain) ``current_word`` are excluded
        from the check so that the word currently being placed does not
        block itself.

        Args:
            char: Single character being considered for placement.
            position: ``(row, col)`` index into the puzzle grid.
            current_word: Text of the word currently being placed, used to
                skip self-referencing sub-word checks.  Defaults to None.

        Returns:
            True if the placement does not create any new duplicate.
        """
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
        return before_ct == after_ct

    def capture_fragments(self, radius: int, position: tuple[int, int]) -> list[str]:
        """Extract character strings along all four axes through ``position``.

        Four fragments are returned — one for each pair of opposing
        directions: diagonal (top-left ↔ bottom-right), horizontal
        (left ↔ right), vertical (top ↔ bottom), and anti-diagonal
        (bottom-left ↔ top-right).  The cell at ``position`` is replaced
        with the sentinel ``"*"`` so the caller can later substitute the
        candidate character without a second grid read.  Cells that fall
        outside the grid boundaries are skipped.

        Args:
            radius: Half-width of the capture window.  Typically the length
                of the longest already-placed word.
            position: ``(row, col)`` centre of the capture window.

        Returns:
            A list of exactly four strings, each representing one axis.
        """
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
            for r, c in zip(row_range, col_range, strict=False):
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
        """Check whether ``word`` can be laid down from ``position`` in ``direction``.

        A placement is valid only if every cell along the path is either
        empty or already contains the matching character, is within grid
        bounds, and is ACTIVE on the mask.

        Args:
            word: The word text to test.
            position: ``(row, col)`` starting cell.
            direction: The :class:`~word_search_generator.core.word.Direction`
                that defines the per-character row/col step.

        Returns:
            A list of ``(row, col)`` coordinates for each letter if the
            word fits; an empty list otherwise.
        """
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
        """Collect every valid direction from ``position`` and pick one at random.

        Secret words are tested against ``secret_directions``; all other
        words use the game's primary direction set.

        Args:
            word: The :class:`~word_search_generator.core.word.Word` to place.
            position: ``(row, col)`` starting cell that has already been
                verified as available by the caller.

        Returns:
            A ``(direction_name, coordinates)`` tuple for the chosen fit.

        Raises:
            WordFitError: If no direction produces a valid fit.
            RuntimeError: If ``word`` is secret but ``secret_directions``
                is empty or missing.
        """
        fits: Fits = []
        # check all directions for level
        if word.secret:
            possible_directions: DirectionSet | None = getattr(
                self.game, "secret_directions", None
            )
            if not possible_directions:
                raise RuntimeError("Secret words require non-empty secret_directions")
        else:
            possible_directions: DirectionSet = self.game.directions

        for d in possible_directions:
            coords = self.test_a_fit(word.text, position, d)
            if coords:
                fits.append((Direction(d).name, coords))
        # if the word fits, pick a random fit for placement
        if not fits:
            raise WordFitError
        return random.choice(fits)

    def fill_words(self) -> None:
        """Attempt to place every game word into the puzzle grid.

        Hidden words are tried first, then secret words.  Each word is
        validated against the game's validator list before placement is
        attempted; words that fail validation or exhaust all retry
        attempts are silently skipped.  Placement stops early once
        ``MAX_PUZZLE_WORDS`` words have been successfully placed.
        """
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
            # Handle graceful failure from retry decorator (returns None on failure)
            if fit is not None and fit:
                placed_words.append(word.text)
            if len(placed_words) == self.game.MAX_PUZZLE_WORDS:
                break

    @retry()
    def try_to_fit_word(self, word: Word) -> bool | None:
        """Attempt a single placement of ``word`` at a random grid cell.

        A random ``(row, col)`` is chosen.  If that cell is occupied by a
        different character or is INACTIVE on the mask a
        :exc:`~word_search_generator.core.generator.WordFitError` is raised
        so the :func:`~word_search_generator.core.generator.retry` decorator
        can try again.  On success the word's metadata (start position,
        direction, coordinates) is updated in place.

        If placing a character would create a duplicate of an already-placed
        word the entire partial placement is rolled back before raising.

        Args:
            word: The word to place.

        Returns:
            True if the word was successfully placed.  The ``@retry``
            wrapper returns None when all attempts are exhausted.

        Raises:
            WordFitError: When the randomly chosen cell or direction does
                not yield a valid placement (caught by ``@retry``).
        """
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
        """Fill every empty ACTIVE cell with a random alphabet character.

        Each candidate character is checked via :meth:`no_duped_words`
        before it is committed; a new random character is drawn until one
        passes, guaranteeing the finished grid contains no unintended
        duplicate words.
        """
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
                        random_char = random.choice(self.alphabet)
                        if self.no_duped_words(random_char, (row, col)):
                            self.puzzle[row][col] = random_char
                            break
