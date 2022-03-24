import copy
import random
import string
from typing import Optional

from word_search_generator import config
from word_search_generator.types import Fit, Fits, Key, KeyInfo, Puzzle

ALPHABET = list(string.ascii_uppercase)


def out_of_bounds(width: int, height: int, position: tuple[int, int]) -> bool:
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


def check_for_dupes_at_position(
    puzzle: Puzzle, char: str, position: tuple[int, int], words: set[str]
):
    # calculate how large of a search radius to check
    # based off of the longest word
    radius = max([len(word) for word in words])
    puzzle_size = len(puzzle)
    # track each part/end of the search radius for each direction
    parts = []
    for rmove, cmove in config.dir_moves.values():
        row, col = position
        letters = []
        for _ in range(radius):
            letters.append(puzzle[row][col])
            row += rmove
            col += cmove
            if out_of_bounds(puzzle_size, puzzle_size, (row, col)):
                break
        parts.append("".join(letters))
        print(f"{(row, col)} => {parts=}")
    combined_parts = []
    adjusted_parts = []
    for i, part in enumerate(parts[4:]):
        if parts[i][0] == "•":
            p1 = parts[i][::-1]
        else:
            p1 = parts[i]
        if part[-1] == "•":
            p2 = part[::-1]
        else:
            p2 = part
        r = p1 + p2[1:]
        combined_parts.append(r)
        adjusted_parts.append(r[: len(r) // 2] + char + r[len(r) // 2 + 1 :])
        # print(f"{combined_parts=}")
        # print(f"{adjusted_parts=}")
        # count how many words are already present in pos search area before adding char
        start_ct = sum([1 for word in words if word in combined_parts])
        # count how many words are already present in pos search area after adding char
        change_ct = sum([1 for word in words if word in adjusted_parts])
        # for word in words:
        #     if word in combined_parts:
        #         # print(f"{word} found in {combined_parts=}")
        #         start_ct += 1
        #     if word in adjusted_parts:
        #         # print(f"{word} found in {adjusted_parts=}")
        #         change_ct += 1
    # print(f"{start_ct=} : {change_ct=}")
    # if any duplicate words were created by adding
    # `char` return false and try again
    print(f"{combined_parts=}")
    if start_ct == change_ct:
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
        # print(f"{word=}")
        # for r in puzzle:
        #     print(" ".join(r))
        # track how many times a word has been tried to speed execution
        tries = 0
        # try to find a fit in the puzzle for the current word
        while tries < config.max_fit_tries:
            # pick a random row and column to try
            row = int(random.randint(0, size - 1))
            col = int(random.randint(0, size - 1))
            # try and find a directional fit using the starting coordinates
            fit = find_a_fit(puzzle, word, (row, col), level)
            work_puzzle = copy.deepcopy(puzzle)
            if fit:
                # print(f"{fit=}")
                d, coords = fit
                # add word letters to a temp work puzzle at the
                # fit coordinates make sure no duplicates are created
                for i, char in enumerate(word):
                    check_row = coords[i][0]
                    check_col = coords[i][1]
                    dupes = check_for_dupes_at_position(
                        work_puzzle, char, (check_row, check_col), words
                    )
                    # print(f"point {(check_row, check_col)} is {dupes}")
                    if dupes:
                        work_puzzle[check_row][check_col] = char
                    else:
                        work_puzzle = copy.deepcopy(puzzle)
                        break
                # for r in work_puzzle:
                #     print(" ".join(r))
            if work_puzzle != puzzle:
                puzzle = copy.deepcopy(work_puzzle)
                # update placement info for word
                key[word] = {"start": (row, col), "direction": d}
                # go to next word
                break
            else:
                # if there was no fit at starting coordinates try again
                tries += 1
    return (puzzle, key)


def no_matching_neighbors(puzzle: Puzzle, char: str, position: tuple[int, int]) -> bool:
    """Ensure no neighboring cells have save character to limit the
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


def fill_blanks(puzzle: Puzzle, words: set[str]) -> Puzzle:
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
                            work_puzzle, random_char, (row, col), words
                        ):
                            work_puzzle[row][col] = random_char
                            break
    return work_puzzle
