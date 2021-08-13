import copy
import random
import string

from . import config


def calc_puzzle_size(words: set, level: int) -> int:
    """Calculate the puzzle grid size based on longest word, word count and level.

    Args:
        words (set): Words to be placed in the puzzle.
        level (int): Puzzle difficulty level.

    Returns:
        int: Final puzzle grid size.
    """
    # get the len of the longest word
    longest = max(set(len(word) for word in words))
    # calculate multipler for larger word list so that most have room to fit
    multiplier = len(words) / 15 if len(words) > 15 else 1
    # set the final puzzle size base on level
    if level == 1:
        size = int((longest + 2) * multiplier)
    elif level == 2:
        size = int((longest + 4) * multiplier)
    else:
        size = int((longest + 8) * multiplier)
    # limit size to max
    if size > config.max_puzzle_size:
        size = config.max_puzzle_size
    return size


def test_a_fit(puzzle: list, word: str, row: int, col: int, dir: str) -> list:
    """Test if word fits in the puzzle at the specified
    coordinates heading in the specified direction.

    Args:
        puzzle (list): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        row (int): Start position row.
        col (int): Start position column.
        dir (str): Direction word is heading.

    Returns:
        list: Coordinates for each letter of the word.
    """
    coords = []
    # iterate over each letter in the word
    for char in word:
        # if the current puzzle space is empty or if letters match
        if puzzle[row][col] == "•" or puzzle[row][col] == char:
            # add the coordinates to the list
            coords.append((row, col))
        else:
            # if the current puzzle spot is already filled cancel fit test
            return False

        # adjust the coordinates along the correction path for this direction
        row += config.dir_moves[dir][0]
        col += config.dir_moves[dir][1]
        # if new coordinates are off of board cancel fit test
        if row < 0 or col < 0 or row > len(puzzle) - 1 or col > len(puzzle[0]) - 1:
            return False

    return coords


def find_a_fit(puzzle: list, word: str, row: int, col: int, level: int) -> tuple:
    """Look for a fit for `word` in the current puzzle.

    Args:
        puzzle (list): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        row (int): Start position row.
        col (int): Start position column.
        level (int): Puzzle difficulty level.

    Returns:
        tuple: Random direction and coordinates for `word` to fit in puzzle.
    """
    fits = {}
    # check all directions for level
    for dir in config.level_dirs[level]:
        coords = test_a_fit(puzzle, word, row, col, dir)
        if coords:
            fits[dir] = coords
    # if the word fit in the puzzle pick a random fit
    if fits:
        return random.choice(list(fits.items()))
    else:
        return False


def fill_words(words: set, level: int, size: int = None) -> dict:
    """Fill the puzzle with the supplied `words`.
    Some words will be skipped if they don't fit.

    Args:
        words (set): Words to be placed in the puzzle.
        level (int, optional): Puzzle difficulty level.
        size (int, optional): Final puzzle grid size.

    Returns:
        dict: Completed puzzle, puzzle aanswer key, final word placements.
    """
    # calculate the puzzle size based on input or words
    size = size if size else calc_puzzle_size(words, level)

    # setup empty puzzle to hold all letters and placement to hold fit details
    puzzle = [["•"] * size for _ in range(size)]
    key = {}

    # try to place each word on the puzzle
    for word in words:
        # track how many times a word has been tried to speed execution
        tries = 0
        # try to find a fit in the puzzle for the current word
        while tries < 100:
            # pick a random row and column to try
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            # try and find a directional fit using the starting coordinates
            fit = find_a_fit(puzzle, word, row, col, level)
            if fit:
                dir, coords = fit
                # add word letters to the puzzle at the fit coordinates
                for i, char in enumerate(word):
                    puzzle[coords[i][0]][coords[i][1]] = char
                # update placement info for word
                # increase row and col by one so count is normal
                key[word] = {"start": (row + 1, col + 1), "dir": dir}
                # go to next word
                break
            # if there was no fit at starting coordinates try again
            tries += 1
    # make a copy of the puzzle answer key
    solution = copy.deepcopy(puzzle)
    # fill in the empty spots with random characters
    puzzle = fill_blanks(puzzle)
    # return the completed puzzle, solution puzzle, and answer key
    return {"puzzle": puzzle, "solution": solution, "key": key}


def no_matching_neighbors(puzzle: list, char: str, row: int, col: int) -> bool:
    """Ensure no neighboring cells have save to limit the
    very small chance of a duplicate word.

    Args:
        puzzle (list): Current puzzle state.
        char (str): Random "fill-in" characer to check against neighbors.
        row (int): Current row in puzzle.
        col (int): Current column in puzzle.

    Returns:
        bool: True is no neighbors match `char`.
    """
    for dir in config.dir_moves:
        test_row = row + config.dir_moves[dir][0]
        test_col = col + config.dir_moves[dir][1]
        if (
            test_row < 0
            or test_col < 0
            or test_row > len(puzzle) - 1
            or test_col > len(puzzle[0]) - 1
        ):
            continue
        if char == puzzle[test_row][test_col]:
            return False
    return True


def fill_blanks(puzzle: list) -> list:
    """Fill in the empty puzzle spaces with random characters.

    Args:
        puzzle (list): Current puzzle state.

    Returns:
        list: A complete word search puzzle.
    """
    alphabet = list(string.ascii_uppercase)
    # iterate over the entire puzzle
    for row in range(len(puzzle)):
        for col in range(len(puzzle[0])):
            # if the current spot is empty
            if puzzle[row][col] == "•":
                # fill it with a random character
                while True:
                    random_char = random.choice(alphabet)
                    if no_matching_neighbors(puzzle, random_char, row, col):
                        puzzle[row][col] = random_char
                        break
    return puzzle
