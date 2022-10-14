import copy
import random
import string
from math import log2
from typing import Optional, Sized

from word_search_generator import config
from word_search_generator.types import (
    DirectionSet,
    Fit,
    Fits,
    Key,
    KeyInfo,
    Position,
    Puzzle,
    Wordlist,
)

ALPHABET = list(string.ascii_uppercase)


class WordFitError(Exception):
    pass


def retry(func):
    """Retry fitting word into puzzle. Hat tip to Bob Belderbos @bbelderbos"""

    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < config.max_fit_tries:
            try:
                return func(*args, **kwargs)
            except Exception:
                attempt += 1
        return (kwargs["puzzle"], kwargs["key"])

    return wrapper


def out_of_bounds(width: int, height: int, position: tuple[int, int]) -> bool:
    """Check to make sure `position` is still on the current puzzle.

    Args:
        width (int): Puzzle board width.
        height (int): Puzzle board height.
        position (tuple[int, int]): Position to check.

    Returns:
        bool: If `position` is on the board.
    """
    row, col = position
    if row < 0 or col < 0 or row > height - 1 or col > width - 1:
        return True
    return False


def calc_puzzle_size(words: Wordlist, level: Sized, size: Optional[int] = None) -> int:
    """Calculate the puzzle grid size.

    Based on longest word, word count, and level.

    Args:
        words (set[str]): Words to be placed in the puzzle.
        level (int): Puzzle difficulty level.
        size (Optional[int], optional): Puzzle size.

    Returns:
        int: Puzzle grid size.
    """
    if not size:
        longest = max(10, len(max(words, key=len)))
        # calculate multiplier for larger word lists so that most have room to fit
        multiplier = len(words) / 15 if len(words) > 15 else 1
        # level lengths in config.py are nice multiples of 2
        l_size = log2(len(level)) if level else 1  # protect against log(0) in tests
        size = round(longest + l_size * 2 * multiplier)
    return size


def capture_all_paths_from_position(
    puzzle: Puzzle, position: tuple[int, int], placed_words: list[str]
) -> list[list[str]]:
    """Capture all directional strings based on length of longest word.

    Args:
        puzzle (Puzzle): Current puzzle state.
        position (tuple[int, int]): Current position on the board.
        placed_words (list[str]): Current words placed in puzzle.

    Returns:
        list[list[str]]: Left and right parts of the search string
        for each direction.
    """
    puzzle_size = len(puzzle)
    # calculate how large of a search radius to check (length of each path)
    radius = max([len(word) for word in placed_words]) if placed_words else 0
    # track each part (start/end) of the search radius for each direction
    # [N, S], [SW, NE] [W, E], [NW, SE]
    paths: list[list[str]] = [["", ""], ["", ""], ["", ""], ["", ""]]
    # follow each direction and capture all characters in that path
    for i, (direction_letter, direction_coord) in enumerate(
        config.Direction.__members__.items()
    ):
        row, col = position
        chars: list[str] = []
        for _ in range(radius):
            chars.append(puzzle[row][col])
            row += direction_coord.r_move
            col += direction_coord.c_move
            if out_of_bounds(puzzle_size, puzzle_size, (row, col)):
                break
            # add the captured string of characters to the correct
            # spot in the paths lists, and reverse if needed
        if direction_letter in ["N", "NW", "W", "SW"]:
            paths[i % 4][0] = "".join(chars[1:][::-1])
        else:
            paths[i % 4][1] = "".join(chars[1:])
    return paths


def check_for_dupes_at_position(
    puzzle: Puzzle, char: str, position: tuple[int, int], placed_words: list[str]
) -> bool:
    """Make sure that adding `char` at `position` will not create a
    duplicate of any word already placed in the puzzle.

    Args:
        puzzle (Puzzle): Current puzzle state.
        char (str): Character to check in `position`.
        position (tuple[int, int]): Position in the puzzle to check.
        placed_words (set[str]): Current words placed in the puzzle.

    Returns:
        bool: If `char` is valid at `pos`.
    """
    # follow each direction and capture all characters in that path
    paths = capture_all_paths_from_position(puzzle, position, placed_words)
    before_ct = after_ct = 0
    for word in placed_words:
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
    puzzle: Puzzle, word: str, position: Position, direction: config.Direction
) -> list[tuple[int, int]]:
    """Test if word fits in the puzzle at the specified
    coordinates heading in the specified direction.

    Args:
        puzzle (Puzzle): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        position (tuple[int, int]): Word (row, column) start position.
        direction (Direction): Direction word is heading.

    Returns:
        list[tuple[int, int]]: Coordinates for each letter of the word.
    """
    coordinates = []
    row, col = position
    # iterate over each letter in the word
    for char in word:
        # if the current puzzle space is empty or if letters match
        if puzzle[row][col] == "" or puzzle[row][col] == char:
            coordinates.append((row, col))
        else:
            return []
        # adjust the coordinates along the word path for direction
        row += direction.r_move
        col += direction.c_move
        # if new coordinates are off of puzzle cancel fit test
        if row < 0 or col < 0 or row > len(puzzle) - 1 or col > len(puzzle[0]) - 1:
            return []
    return coordinates


def find_a_fit(
    puzzle: Puzzle, word: str, position: Position, level: DirectionSet
) -> Fit:
    """Look for a fit for `word` in the current puzzle.

    Args:
        puzzle (Puzzle): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        position (tuple[int, int]): Word (row, column) start position.
        level (DirectionSet): Puzzle difficulty level.

    Returns:
        Fit: A random position where the word fits in the puzzle.
    """
    fits: Fits = {}
    random_direction = None
    # check all directions for level
    for d in level:
        coords = test_a_fit(puzzle, word, position, d)
        if coords:
            fits[config.Direction(d).name] = coords
    # if the word fits, pick a random fit for placement
    if fits:
        random_direction = random.choice(list(fits.items()))
    return random_direction


def fill_words(
    words: Wordlist,
    possible_directions: DirectionSet,
    size: int,
    secret_words: Wordlist,
    secret_directions: Optional[DirectionSet] = None,
) -> tuple[Puzzle, Key]:
    """Fill `puzzle` with the supplied `words`.
    Some words will be skipped if they don't fit.

    Args:
        words (set[str]): Words to be placed in the puzzle.
        possible_directions (DirectionSet): Allowed directions for word placement.
        size (int, optional): Final puzzle grid size.
        secret_words (set[str]): Hidden words to be placed in the puzzle.
        secret_directions (DirectionSet, optional): Allowed directions for secret word
            placement, if different from those allowed for normal words.

    Returns:
        tuple[Puzzle, Key]: Current puzzle and puzzle answer key.
    """
    # calculate the puzzle size and setup a new empty puzzle
    if not secret_directions:
        secret_directions = possible_directions
    size = calc_puzzle_size(words.union(secret_words), possible_directions, size)
    puzzle = [[""] * size for _ in range(size)]
    key: dict[str, KeyInfo] = {}

    # try to place each word on the puzzle
    for word in words:
        puzzle, key = try_to_fit_word(
            word=word, puzzle=puzzle, key=key, level=possible_directions, size=size
        )
    # try to place each secret word on the puzzle
    # "real" words are given priority; this is always done after those have been placed
    for word in secret_words:
        puzzle, key = try_to_fit_word(
            word=word,
            puzzle=puzzle,
            key=key,
            level=secret_directions,
            size=size,
            secret=True,
        )
    return (puzzle, key)


@retry
def try_to_fit_word(
    word: str,
    puzzle: Puzzle,
    key: Key,
    level: DirectionSet,
    size: int,
    secret: bool = False,
) -> tuple[Puzzle, Key]:
    """Try to fit `word` at randomized coordinates.
    @retry wrapper controls the number of attempts"""
    pos = Position(random.randint(0, size - 1), random.randint(0, size - 1))
    # try and find a directional fit using the starting coordinates
    fit = find_a_fit(puzzle, word, pos, level)
    work_puzzle = copy.deepcopy(puzzle)
    if not fit:
        raise WordFitError
    d, coords = fit
    # add word letters to a temp work puzzle at the
    # fit coordinates make sure no duplicates are created
    for i, char in enumerate(word):
        check_row = coords[i][0]
        check_col = coords[i][1]
        if check_for_dupes_at_position(
            work_puzzle, char, (check_row, check_col), list(key.keys())
        ):
            work_puzzle[check_row][check_col] = char
        else:
            work_puzzle = copy.deepcopy(puzzle)
            break

    if work_puzzle == puzzle:
        raise WordFitError
    puzzle = copy.deepcopy(work_puzzle)
    # update placement info for word
    key[word] = {"start": pos, "direction": d, "secret": secret}
    return (puzzle, key)


def no_matching_neighbors(puzzle: Puzzle, char: str, position: tuple[int, int]) -> bool:
    """Ensure no neighboring cells have same character to limit the
    very small chance of a duplicate word.

    Args:
        puzzle (Puzzle): Current puzzle state.
        char (str): Random "fill-in" character to check against neighbors.
        position (tuple[int, int]): Word (row, column) start position.

    Returns:
        bool: True is no neighbors match `char`.
    """
    row, col = position
    # check all 8 possible neighbors
    for d in config.Direction:
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


def fill_blanks(puzzle: Puzzle, placed_words: list[str]) -> Puzzle:
    """Fill empty puzzle spaces with random characters.

    Args:
        puzzle (Puzzle): Current puzzle state.
        placed_words (set[str]): Puzzle word list.

    Returns:
        Puzzle: A complete word search puzzle.
    """
    work_puzzle = copy.deepcopy(puzzle)
    # iterate over the entire puzzle
    for row in range(len(work_puzzle)):
        for col in range(len(work_puzzle[0])):
            # if the current spot is empty fill with random character
            if work_puzzle[row][col] == "":
                while True:
                    random_char = random.choice(ALPHABET)
                    if no_matching_neighbors(work_puzzle, random_char, (row, col)):
                        if check_for_dupes_at_position(
                            work_puzzle, random_char, (row, col), placed_words
                        ):
                            work_puzzle[row][col] = random_char
                            break
    return work_puzzle
