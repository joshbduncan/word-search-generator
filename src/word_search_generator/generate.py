from __future__ import annotations

import copy
import random
import string
import sys
from math import log2
from typing import TYPE_CHECKING, List, Optional, Sized, Tuple

from word_search_generator.config import max_fit_tries
from word_search_generator.types import Direction, Fit, Fits, Puzzle, Word, Wordlist

if TYPE_CHECKING:  # pragma: no cover
    from word_search_generator import WordSearch

ALPHABET = list(string.ascii_uppercase)


class WordFitError(Exception):
    pass


def retry(func):
    """Retry fitting word into puzzle. Hat tip to Bob Belderbos @bbelderbos"""

    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < max_fit_tries:
            try:
                return func(*args, **kwargs)
            except Exception:
                attempt += 1
        return

    return wrapper


def out_of_bounds(puzzle: WordSearch, position: Tuple[int, int]) -> bool:
    """Validate `position` is within the current puzzle bounds."""
    width = height = puzzle.size
    row, col = position
    if row < 0 or col < 0 or row > height - 1 or col > width - 1:
        return True
    return False


def calc_puzzle_size(words: Wordlist, level: Sized, size: Optional[int] = None) -> int:
    """Calculate the puzzle grid size."""
    all_words = list(word.text for word in words)
    longest_word_length = len(max(all_words, key=len))
    shortest_word_length = len(min(all_words, key=len))
    if not size:
        longest = max(10, longest_word_length)
        # calculate multiplier for larger word lists so that most have room to fit
        multiplier = len(all_words) / 15 if len(all_words) > 15 else 1
        # level lengths in config.py are nice multiples of 2
        l_size = log2(len(level)) if level else 1  # protect against log(0) in tests
        size = round(longest + l_size * 2 * multiplier)
    else:
        if size < shortest_word_length:
            print(
                "Puzzle sized adjust to fit word with the shortest length.",
                file=sys.stderr,
            )
            size = shortest_word_length + 1
    return size


def capture_all_paths_from_position(
    puzzle: WordSearch, position: Tuple[int, int]
) -> List[List[str]]:
    """Capture strings from `position` in each direction."""
    placed_words = tuple(word.text for word in puzzle.placed_words)
    # calculate how large of a search radius to check (length of each path)
    radius = max([len(word) for word in placed_words]) if placed_words else 0
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
            if out_of_bounds(puzzle, (row, col)):
                break
            chars.append(puzzle.solution[row][col])
            row += direction_coord.r_move
            col += direction_coord.c_move
            # add the captured string of characters to the correct
            # spot in the paths lists, and reverse if needed
        if direction_letter in ["N", "NW", "W", "SW"]:
            paths[i % 4][0] = "".join(chars[1:][::-1])
        else:
            paths[i % 4][1] = "".join(chars[1:])
    return paths


def no_duped_words(puzzle: WordSearch, char: str, position: Tuple[int, int]) -> bool:
    """Make sure that adding `char` at `position` will not create a
    duplicate of any word already placed in the puzzle."""
    paths = capture_all_paths_from_position(puzzle, position)
    before_ct = after_ct = 0
    for word in list(puzzle.key.keys()):
        for path in paths:
            before = "•".join(path)
            after = char.join(path)
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


def test_a_fit(
    puzzle: WordSearch, word: str, position: Tuple[int, int], direction: Direction
) -> List[Tuple[int, int]]:
    """Test if word fits in the puzzle at the specified
    coordinates heading in the specified direction."""
    coordinates = []
    row, col = position
    # iterate over each letter in the word
    for char in word:
        # if the current puzzle space is empty or if letters match
        if puzzle.solution[row][col] == "" or puzzle.solution[row][col] == char:
            coordinates.append((row, col))
        else:
            return []
        # adjust the coordinates along the word path for direction
        row += direction.r_move
        col += direction.c_move
        # if new coordinates are off of puzzle cancel fit test
        if out_of_bounds(puzzle, (row, col)):
            return []
    return coordinates


def find_a_fit(puzzle: WordSearch, word: str, position: Tuple[int, int]) -> Fit:
    """Look for random place in the puzzle where `word` fits."""
    fits: Fits = {}
    random_direction = None
    # check all directions for level
    for d in puzzle.directions:
        coords = test_a_fit(puzzle, word, position, d)
        if coords:
            fits[Direction(d).name] = coords
    # if the word fits, pick a random fit for placement
    if fits:
        random_direction = random.choice(list(fits.items()))
    return random_direction


def fill_words(puzzle: WordSearch) -> None:
    """Fill `puzzle` with the supplied `words`.
    Some words will be skipped if they don't fit."""
    puzzle._solution = [[""] * puzzle.size for _ in range(puzzle.size)]
    # try to place each word on the puzzle
    for word in puzzle.hidden_words:
        try_to_fit_word(
            puzzle=puzzle,
            word=word,
        )
    # try to place each secret word on the puzzle
    # "real" words are given priority
    # this is always done after those have been placed
    for word in puzzle.secret_words:
        try_to_fit_word(
            puzzle=puzzle,
            word=word,
        )


@retry
def try_to_fit_word(
    puzzle: WordSearch,
    word: Word,
) -> None:
    """Try to fit `word` at randomized coordinates.
    @retry wrapper controls the number of attempts"""
    row = random.randint(0, puzzle.size - 1)
    col = random.randint(0, puzzle.size - 1)
    # try and find a directional fit using the starting coordinates
    fit = find_a_fit(puzzle, word.text, (row, col))
    work_puzzle = copy.deepcopy(puzzle.solution)
    if not fit:
        raise WordFitError
    d, coords = fit
    # add word letters to a temp work puzzle at the
    # fit coordinates make sure no duplicates are created
    for i, char in enumerate(word.text):
        check_row = coords[i][0]
        check_col = coords[i][1]
        if no_duped_words(puzzle, char, (check_row, check_col)):
            work_puzzle[check_row][check_col] = char
        else:
            work_puzzle = copy.deepcopy(puzzle.solution)
            break
    if work_puzzle == puzzle.solution:
        raise WordFitError
    puzzle._solution = copy.deepcopy(work_puzzle)
    # update placement info for word
    word._start_row = row
    word._start_column = col
    word.direction = Direction[d]


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


def fill_blanks(puzzle: WordSearch) -> None:
    """Fill empty puzzle spaces with random characters."""
    puzzle._puzzle = copy.deepcopy(puzzle.solution)
    # iterate over the entire puzzle
    for row in range(len(puzzle._puzzle)):
        for col in range(len(puzzle._puzzle[0])):
            # if the current spot is empty fill with random character
            if puzzle._puzzle[row][col] == "":
                while True:
                    random_char = random.choice(ALPHABET)
                    if no_matching_neighbors(
                        puzzle._puzzle, random_char, (row, col)
                    ) and no_duped_words(puzzle, random_char, (row, col)):
                        puzzle._puzzle[row][col] = random_char
                        break
