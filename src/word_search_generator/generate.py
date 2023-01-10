from __future__ import annotations

import random
import string
from functools import wraps
from typing import TYPE_CHECKING, List, Tuple

from .config import ACTIVE, INACTIVE, max_fit_tries, max_puzzle_words
from .utils import in_bounds
from .word import Direction, Word

if TYPE_CHECKING:  # pragma: no cover
    from . import Puzzle, WordSearch


Fit = Tuple[str, List[Tuple[int, int]]]
Fits = List[Tuple[str, List[Tuple[int, int]]]]


ALPHABET = list(string.ascii_uppercase)


class WordFitError(Exception):
    pass


def retry(retries: int = max_fit_tries):
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


def no_duped_words(
    puzzle: Puzzle, placed_words: set[str], char: str, position: tuple[int, int]
) -> bool:
    """Make sure that adding `char` at `position` will not create a
    duplicate of any word already placed in the puzzle."""
    if not placed_words:
        return True
    # calculate how large of a search radius to check
    radius = len(max(placed_words, key=len))
    # track each directional fragment of characters
    fragments = capture_fragments(puzzle, radius, position)
    # check to see if any duped words are now present
    before_ct = after_ct = 0
    for word in placed_words:
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


def capture_fragments(
    puzzle: Puzzle, radius: int, position: tuple[int, int]
) -> list[str]:
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
            if in_bounds(n_row, n_col, len(puzzle), len(puzzle)):
                found = puzzle[n_row][n_col] if puzzle[n_row][n_col] else " "
                fragments[n] = found + fragments[n]
            # right and bottom traveling directions go on the end of the fragment
            n_row = row + (ry * (r + 1))
            n_col = col + (rx * (r + 1))
            if in_bounds(n_row, n_col, len(puzzle), len(puzzle)):
                found = puzzle[n_row][n_col] if puzzle[n_row][n_col] else " "
                fragments[n] += found
    return fragments


def test_a_fit(
    puzzle: Puzzle,
    mask: Puzzle,
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
        if not in_bounds(col, row, len(puzzle), len(puzzle)):
            return []
        # first check if the spot is inactive on the mask
        if mask[row][col] == INACTIVE:
            return []
        # if the current puzzle space is empty or if letters match
        if puzzle[row][col] != "" and puzzle[row][col] != char:
            return []
        coordinates.append((row, col))
        # adjust the coordinates for the next character
        row += direction.r_move
        col += direction.c_move
    return coordinates


def find_a_fit(ws: WordSearch, word: str, position: tuple[int, int]) -> Fit:
    """Look for random place in the puzzle where `word` fits."""
    fits: Fits = []
    # check all directions for level
    for d in ws.directions:
        coords = test_a_fit(ws.puzzle, ws.mask, word, position, d)
        if coords:
            fits.append((Direction(d).name, coords))
    # if the word fits, pick a random fit for placement
    if not fits:
        raise WordFitError
    return random.choice(fits)


def fill_words(ws: WordSearch) -> None:
    """Fill `ws.puzzle` with the supplied `words`.
    Some words will be skipped if they don't fit."""
    # try to place each word on the puzzle
    if ws.hidden_words:
        for word in ws.hidden_words:
            try_to_fit_word(ws=ws, word=word)
            if len(ws.placed_words) == max_puzzle_words:
                break
    # try to place each secret word on the puzzle
    # "real" words are given priority
    # this is always done after those have been placed
    if ws.secret_words:
        for word in ws.secret_words:
            try_to_fit_word(ws=ws, word=word)
            if len(ws.placed_words) == max_puzzle_words:
                break


@retry()
def try_to_fit_word(ws: WordSearch, word: Word) -> None:
    """Try to fit `word` at randomized coordinates.
    @retry wrapper controls the number of attempts"""
    placed_words = {word.text for word in ws.placed_words}
    row = random.randint(0, ws.size - 1)
    col = random.randint(0, ws.size - 1)

    # no need to continue if random coordinate isn't available
    if ws.puzzle[row][col] != "" and ws.puzzle[row][col] != word.text[0]:
        raise WordFitError
    if ws.mask[row][col] == INACTIVE:
        raise WordFitError

    # try and find a directional fit using the starting coordinates if not INACTIVE
    d, coords = find_a_fit(ws, word.text, (row, col))

    # place word characters at fit coordinates
    previous_chars = []  # track previous to backtrack on WordFitError
    for i, char in enumerate(word.text):
        check_row = coords[i][0]
        check_col = coords[i][1]
        previous_chars.append(ws.puzzle[check_row][check_col])
        # no need to check for dupes if characters are the same
        if char == ws.puzzle[check_row][check_col]:
            continue
        # make sure placed character doesn't cause a duped word in the puzzle
        if no_duped_words(ws.puzzle, placed_words, char, (check_row, check_col)):
            ws._puzzle[check_row][check_col] = char
        else:
            # if a duped word was created put previous characters back in place
            for n, previous_char in enumerate(previous_chars):
                ws._puzzle[coords[n][0]][coords[n][1]] = previous_char
            raise WordFitError
    # update word placement info
    word.start_row = row
    word.start_column = col
    word.direction = Direction[d]
    word.coordinates = coords


def fill_blanks(ws: WordSearch) -> None:
    """Fill empty puzzle spaces with random characters."""
    # iterate over the entire puzzle
    placed_words = {word.text for word in ws.placed_words}
    for row in range(ws.size):
        for col in range(ws.size):
            # if the current spot is empty fill with random character
            if ws.puzzle[row][col] == "" and ws.mask[row][col] == ACTIVE:
                while True:
                    random_char = random.choice(ALPHABET)
                    if no_duped_words(ws.puzzle, placed_words, random_char, (row, col)):
                        ws.puzzle[row][col] = random_char
                        break
