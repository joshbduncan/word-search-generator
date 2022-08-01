import copy
import random
import string
from typing import Optional

from word_search_generator import config
from word_search_generator.types import Fit, Fits, Key, KeyInfo, Puzzle

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


def calc_puzzle_size(words: set[str], level: int, size: Optional[int] = None) -> int:
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
        # calculate multipler for larger word lists so that most have room to fit
        multiplier = len(words) / 15 if len(words) > 15 else 1
        size = int(longest + level * 2 * multiplier)
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
    for i, (direction, (rmove, cmove)) in enumerate(config.dir_moves.items()):
        row, col = position
        string = ""
        for _ in range(radius):
            string += puzzle[row][col]
            row += rmove
            col += cmove
            if out_of_bounds(puzzle_size, puzzle_size, (row, col)):
                break
        # add the captured string of characters to the correct
        # spot in the paths lists, and reverse if needed
        if direction in ["N", "NW", "W", "SW"]:
            paths[i % 4][0] = string[1:][::-1]
        else:
            paths[i % 4][1] = string[1:]
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
    puzzle: Puzzle, word: str, position: tuple[int, int], direction: str
) -> list[tuple[int, int]]:
    """Test if word fits in the puzzle at the specified
    coordinates heading in the specified direction.

    Args:
        puzzle (Puzzle): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        position (tuple[int, int]): Word (row, column) start position.
        direction (str): Direction word is heading.

    Returns:
        list[tuple[int, int]]: Coordinates for each letter of the word.
    """
    coordinates = []
    row, col = position
    # iterate over each letter in the word
    for char in word:
        rmove, cmove = config.dir_moves[direction]
        # if the current puzzle space is empty or if letters match
        if puzzle[row][col] == "•" or puzzle[row][col] == char:
            coordinates.append((row, col))
        else:
            return []
        # adjust the coordinates along the word path for direction
        row += rmove
        col += cmove
        # if new coordinates are off of puzzle cancel fit test
        if row < 0 or col < 0 or row > len(puzzle) - 1 or col > len(puzzle[0]) - 1:
            return []
    return coordinates


def find_a_fit(puzzle: Puzzle, word: str, position: tuple[int, int], level: int) -> Fit:
    """Look for a fit for `word` in the current puzzle.

    Args:
        puzzle (Puzzle): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        position (tuple[int, int]): Word (row, column) start position.
        level (int): Puzzle difficulty level.

    Returns:
        Fit: A random position where the word fits in the puzzle.
    """
    fits: Fits = {}
    random_direction = None
    row, col = position
    # check all directions for level
    for d in config.level_dirs[level]:
        coords = test_a_fit(puzzle, word, (row, col), d)
        if coords:
            fits[d] = coords
    # if the word fits, pick a random fit for placement
    if fits:
        random_direction = random.choice(list(fits.items()))
    return random_direction


def fill_words(words: set[str], level: int, size: int) -> tuple[Puzzle, Key]:
    """Fill `puzzle` with the supplied `words`.
    Some words will be skipped if they don't fit.

    Args:
        words (set[str]): Words to be placed in the puzzle.
        level (int): Puzzle difficulty level.
        size (int, optional): Final puzzle grid size.

    Returns:
        tuple[Puzzle, Key]: Current puzzle and puzzle answer key.
    """

    # calculate the puzzle size and setup a new empty puzzle
    size = calc_puzzle_size(words, level, size)
    puzzle = [["•"] * size for _ in range(size)]
    key: dict[str, KeyInfo] = {}

    # try to place each word on the puzzle
    for word in words:
        puzzle, key = try_to_fit_word(
            word=word, puzzle=puzzle, key=key, level=level, size=size
        )
    return (puzzle, key)


@retry
def try_to_fit_word(
    word: str, puzzle: Puzzle, key: Key, level: int, size: int
) -> tuple[Puzzle, Key]:
    """Try to fit `word` at randomized coordinates `times` times."""
    row = int(random.randint(0, size - 1))
    col = int(random.randint(0, size - 1))
    # try and find a directional fit using the starting coordinates
    fit = find_a_fit(puzzle, word, (row, col), level)
    work_puzzle = copy.deepcopy(puzzle)
    if fit:
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
    else:
        puzzle = copy.deepcopy(work_puzzle)
        # update placement info for word
        key[word] = {"start": (row, col), "direction": d}
    return (puzzle, key)


def no_matching_neighbors(puzzle: Puzzle, char: str, position: tuple[int, int]) -> bool:
    """Ensure no neighboring cells have same character to limit the
    very small chance of a duplicate word.

    Args:
        puzzle (Puzzle): Current puzzle state.
        char (str): Random "fill-in" characer to check against neighbors.
        position (tuple[int, int]): Word (row, column) start position.

    Returns:
        bool: True is no neighbors match `char`.
    """
    row, col = position
    # check all 8 possible neighbors
    for d in config.dir_moves:
        test_row = row + config.dir_moves[d][0]
        test_col = col + config.dir_moves[d][1]
        # if test coordinates are off puzzle skip
        if (
            test_row < 0
            or test_col < 0
            or test_row > len(puzzle) - 1
            or test_col > len(puzzle[0]) - 1
        ):
            continue
        # if this neighbor matchs try another character
        if char == puzzle[test_row][test_col]:
            return False
    return True


def fill_blanks(puzzle: Puzzle, placed_words: list[str]) -> Puzzle:
    """Fill empty puzzle spaces with random characters.

    Args:
        puzzle (Puzzle): Current puzzle state.
        words (set[str]): Puzzle word list.

    Returns:
        Puzzle: A complete word search puzzle.
    """
    work_puzzle = copy.deepcopy(puzzle)
    # iterate over the entire puzzle
    for row in range(len(work_puzzle)):
        for col in range(len(work_puzzle[0])):
            # if the current spot is empty fill with random character
            if work_puzzle[row][col] == "•":
                while True:
                    random_char = random.choice(ALPHABET)
                    if no_matching_neighbors(work_puzzle, random_char, (row, col)):
                        if check_for_dupes_at_position(
                            work_puzzle, random_char, (row, col), placed_words
                        ):
                            work_puzzle[row][col] = random_char
                            break
    return work_puzzle
