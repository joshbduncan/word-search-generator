import copy
import random
import string

from word_search_generator import config


def calc_puzzle_size(words: set, level: int, size: int = None) -> int:
    """Calculate the puzzle grid size based on longest word, word count and level.

    Args:
        words (set): Words to be placed in the puzzle.
        level (int): Puzzle difficulty level.
        size (int): User requested size of puzzle.

    Returns:
        int: Final puzzle grid size.
    """
    if not size:
        longest = len(max(words, key=len))
        # calculate multipler for larger word lists so that most have room to fit
        multiplier = len(words) / 15 if len(words) > 15 else 1
        size = int(longest + level * 2 * multiplier)
    # make sure size isn't too small or too big
    if size > config.max_puzzle_size:
        size = config.max_puzzle_size
    elif size < config.min_puzzle_size:
        size = config.min_puzzle_size
    return size


def test_a_fit(puzzle: list, word: str, position: tuple, direction: str) -> list:
    """Test if word fits in the puzzle at the specified
    coordinates heading in the specified direction.

    Args:
        puzzle (list): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        position (tuple): Word (row, column) start position.
        direction (str): Direction word is heading.

    Returns:
        list: Coordinates for each letter of the word.
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


def find_a_fit(puzzle: list, word: str, position: tuple, level: int) -> tuple:
    """Look for a fit for `word` in the current puzzle.

    Args:
        puzzle (list): Current puzzle state.
        word (str): Word to try and fit in the puzzle.
        position (tuple): Word (row, column) start position.
        level (int): Puzzle difficulty level.

    Returns:
        tuple: Random direction and coordinates for `word` to fit in puzzle.
    """
    fits = {}
    row, col = position
    # check all directions for level
    for d in config.level_dirs[level]:
        coords = test_a_fit(puzzle, word, (row, col), d)
        if coords:
            fits[d] = coords
    # if the word fit in the puzzle pick a random fit
    if fits:
        return random.choice(list(fits.items()))
    else:
        return ()


def fill_words(words: set, level: int, size: int = None) -> dict:
    """Fill the puzzle with the supplied `words`.
    Some words will be skipped if they don't fit.

    Args:
        words (set): Words to be placed in the puzzle.
        level (int, optional): Puzzle difficulty level.
        size (int, optional): Final puzzle grid size.

    Returns:
        dict: Completed puzzle, puzzle answer key, final word placements.
    """
    # calculate the puzzle size and setup a new empty puzzle
    size = calc_puzzle_size(words, level, size)
    puzzle = [["•"] * size for _ in range(size)]
    key = {}

    # try to place each word on the puzzle
    for word in words:
        # track how many times a word has been tried to speed execution
        tries = 0
        # try to find a fit in the puzzle for the current word
        while tries < config.max_fit_tries:
            # pick a random row and column to try
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            # try and find a directional fit using the starting coordinates
            fit = find_a_fit(puzzle, word, (row, col), level)
            if fit:
                d, coords = fit
                # add word letters to the puzzle at the fit coordinates
                for i, char in enumerate(word):
                    puzzle[coords[i][0]][coords[i][1]] = char
                # update placement info for word
                # increase row and col by one so they are 1-based
                key[word] = {"start": (row, col), "direction": d}
                # go to next word
                break
            # if there was no fit at starting coordinates try again
            tries += 1
    # make a copy of the puzzle answer key, fill in the puzzle with random characters
    solution = copy.deepcopy(puzzle)
    puzzle = fill_blanks(puzzle)
    return {"puzzle": puzzle, "solution": solution, "key": key}


def no_matching_neighbors(puzzle: list, char: str, position: tuple) -> bool:
    """Ensure no neighboring cells have save to limit the
    very small chance of a duplicate word.

    Args:
        puzzle (list): Current puzzle state.
        char (str): Random "fill-in" characer to check against neighbors.
        position (tuple): Word (row, column) start position.

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
            # if the current spot is empty fill with random character
            if puzzle[row][col] == "•":
                while True:
                    random_char = random.choice(alphabet)
                    if no_matching_neighbors(puzzle, random_char, (row, col)):
                        puzzle[row][col] = random_char
                        break
    return puzzle
