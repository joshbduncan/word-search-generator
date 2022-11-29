from __future__ import annotations

import copy
import random
import string
from functools import wraps
from typing import TYPE_CHECKING, List, Tuple

from .config import ACTIVE, INACTIVE, max_fit_tries
from .utils import in_bounds
from .word import Direction, Fit, Fits, Word, Wordlist

if TYPE_CHECKING:  # pragma: no cover
    from . import Puzzle, WordSearch

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


def capture_all_paths_from_position(
    puzzle: Puzzle, placed_words: Wordlist, position: Tuple[int, int]
) -> List[List[str]]:
    """Capture strings from `position` in each direction."""
    # calculate how large of a search radius to check (length of each path)
    radius = max([len(word.text) for word in placed_words]) if placed_words else 0
    # track each part (start/end) of the search radius for each direction
    # [N, S], [SW, NE] [W, E], [NW, SE]
    paths: List[List[str]] = [["", ""], ["", ""], ["", ""], ["", ""]]
    # follow each direction and capture all characters in that path
    for i, (direction_letter, direction_coord) in enumerate(
        Direction.__members__.items()
    ):
        row, col = position
        chars: List[str] = []
        for _ in range(radius):
            if not in_bounds(col, row, len(puzzle), len(puzzle)):
                break
            chars.append(puzzle[row][col])
            row += direction_coord.r_move
            col += direction_coord.c_move
            # add the captured string of characters to the correct
            # spot in the paths lists, and reverse if needed
        if direction_letter in ["N", "NW", "W", "SW"]:
            paths[i % 4][0] = "".join(chars[1:][::-1])
        else:
            paths[i % 4][1] = "".join(chars[1:])
    return paths


def no_duped_words(
    puzzle: Puzzle, placed_words: Wordlist, char: str, position: Tuple[int, int]
) -> bool:
    """Make sure that adding `char` at `position` will not create a
    duplicate of any word already placed in the puzzle."""
    paths = capture_all_paths_from_position(puzzle, placed_words, position)
    before_ct = after_ct = 0
    for word in placed_words:
        for path in paths:
            before = "•".join(path)
            after = char.join(path)
            if word.text in before:
                before_ct += 1
            if word.text[::-1] in before:
                before_ct += 1
            if word.text in after:
                after_ct += 1
            if word.text[::-1] in after:
                after_ct += 1
    if before_ct == after_ct:
        return True
    return False


def test_a_fit(
    puzzle: Puzzle,
    mask: Puzzle,
    word: str,
    position: Tuple[int, int],
    direction: Direction,
) -> List[Tuple[int, int]]:
    """Test if word fits in the puzzle at the specified
    coordinates heading in the specified direction."""
    coordinates = []
    row, col = position
    # iterate over each letter in the word
    for char in word:
        # first check if the spot is inactive on the mask
        if mask[row][col] == INACTIVE:
            return []
        # if the current puzzle space is empty or if letters match
        if puzzle[row][col] == "" or puzzle[row][col] == char:
            coordinates.append((row, col))
        else:
            return []
        # adjust the coordinates along the word path for direction
        row += direction.r_move
        col += direction.c_move
        # if new coordinates are off of puzzle cancel fit test
        if not in_bounds(col, row, len(puzzle), len(puzzle)):
            return []
    return coordinates


def find_a_fit(ws: WordSearch, word: str, position: Tuple[int, int]) -> Fit:
    """Look for random place in the puzzle where `word` fits."""
    fits: Fits = {}
    random_direction = None
    # check all directions for level
    for d in ws.directions:
        coords = test_a_fit(ws.puzzle, ws.mask, word, position, d)
        if coords:
            fits[Direction(d).name] = coords
    # if the word fits, pick a random fit for placement
    if fits:
        random_direction = random.choice(list(fits.items()))
    return random_direction


def fill_words(ws: WordSearch) -> None:
    """Fill `ws.puzzle` with the supplied `words`.
    Some words will be skipped if they don't fit."""
    # try to place each word on the puzzle
    for word in ws.hidden_words:
        try_to_fit_word(
            ws=ws,
            word=word,
        )
    # try to place each secret word on the puzzle
    # "real" words are given priority
    # this is always done after those have been placed
    for word in ws.secret_words:
        try_to_fit_word(
            ws=ws,
            word=word,
        )


@retry()
def try_to_fit_word(
    ws: WordSearch,
    word: Word,
) -> None:
    """Try to fit `word` at randomized coordinates.
    @retry wrapper controls the number of attempts"""

    row = random.randint(0, ws.size - 1)
    col = random.randint(0, ws.size - 1)
    if ws.mask[row][col] == INACTIVE:
        raise WordFitError
    # try and find a directional fit using the starting coordinates if not INACTIVE
    fit = find_a_fit(ws, word.text, (row, col))
    work_puzzle = copy.deepcopy(ws.puzzle)
    if not fit:
        raise WordFitError
    d, coords = fit
    # add word letters to a temp work puzzle at the
    # fit coordinates make sure no duplicates are created
    for i, char in enumerate(word.text):
        check_row = coords[i][0]
        check_col = coords[i][1]
        if no_duped_words(ws.puzzle, ws.placed_words, char, (check_row, check_col)):
            work_puzzle[check_row][check_col] = char
        else:
            work_puzzle = copy.deepcopy(ws.puzzle)
            break
    if work_puzzle == ws.puzzle:
        raise WordFitError
    ws._puzzle = copy.deepcopy(work_puzzle)
    # update placement info for word
    word.start_row = row
    word.start_column = col
    word.direction = Direction[d]
    word.coordinates = coords


def no_matching_neighbors(puzzle: Puzzle, char: str, position: Tuple[int, int]) -> bool:
    """Ensure no neighboring cells have same character to limit the
    very small chance of a duplicate word."""
    row, col = position
    # check all 8 possible neighbors
    for d in Direction:
        test_row = row + d.r_move
        test_col = col + d.c_move
        # if test coordinates are off puzzle skip
        if (
            test_row < 0
            or test_col < 0
            or test_row > len(puzzle) - 1
            or test_col > len(puzzle[0]) - 1
        ):
            continue
        # if this neighbor matches try another character
        if char == puzzle[test_row][test_col]:
            return False
    return True


def fill_blanks(ws: WordSearch) -> None:
    """Fill empty puzzle spaces with random characters."""
    # iterate over the entire puzzle
    for row in range(ws.size):
        for col in range(ws.size):
            # if the current spot is empty fill with random character
            if ws.puzzle[row][col] == "" and ws.mask[row][col] == ACTIVE:
                while True:
                    random_char = random.choice(ALPHABET)
                    if no_matching_neighbors(
                        ws.puzzle, random_char, (row, col)
                    ) and no_duped_words(
                        ws.puzzle, ws.placed_words, random_char, (row, col)
                    ):
                        ws.puzzle[row][col] = random_char
                        break
