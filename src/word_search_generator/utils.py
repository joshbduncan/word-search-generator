import random
import string
from pathlib import Path
from typing import Optional

from colorama import Style, init

from word_search_generator import config
from word_search_generator.types import Key, Puzzle

init()


def cleanup_input(words: str) -> set[str]:
    """Cleanup provided input string. Removing spaces
    one-letter words, and words with punctuation.

    Args:
        words (str): String of words separated by commas, spaces, or new lines.

    Raises:
        TypeError: A string was not provided.
        ValueError: No proper words were provided.

    Returns:
        set[str]: Words to be placed in the puzzle.
    """
    if not isinstance(words, str):
        raise TypeError(
            "Words must be a string separated by spaces, commas, or new lines"
        )
    # remove new lines
    words = words.replace("\n", ",")
    # remove excess spaces and commas
    word_list = ",".join(words.split(" ")).split(",")
    # iterate through all words and pick first set that match criteria
    word_set: set[str] = set()
    while word_list and len(word_set) <= config.max_puzzle_words:
        word = word_list.pop(0)
        if (
            len(word) > 1
            and not contains_punctuation(word)
            and not is_palindrome(word)
            and not word_contains_word(word_set, word.upper())
        ):
            word_set.add(word.upper())
    # if no words were left raise exception
    if not word_set:
        raise ValueError("Use words longer than one-character and without punctuation.")
    return word_set


def contains_punctuation(word):
    """Check to see if puncuation is present in the provided string."""
    return any([True if c in string.punctuation else False for c in word])


def is_palindrome(word: str) -> bool:
    """Check is a word in a palindrome."""
    return word == word[::-1]


def word_contains_word(words: set[str], word: str) -> bool:
    """Make sure `test_word` cannot be found in any word
    in `words`, going forward or backword.
    Args:
        words (str): Current puzzle word list.
        word (str): Word to check for.
    Returns:
        bool: If word was found contained in any word in words.
    """
    for test_word in words:
        if (
            word in test_word.upper()
            or word[::-1] in test_word.upper()
            or test_word.upper() in word
            or test_word.upper()[::-1] in word
        ):
            return True
    return False


def highlight_solution(
    puzzle: Puzzle,
    solution: Optional[Puzzle] = None,
) -> Puzzle:
    """Convert puzzle array of nested lists into a string.

    Args:
        puzzle (Puzzle): he current puzzle state.
        solution (Optional[Puzzle], optional): If a solution is provided
        it will be highlighted in the output. Defaults to None.

    Returns:
        str: The current puzzle as a string.
    """
    output = []
    for r, line in enumerate(puzzle):
        line_chars = []
        # check to see if character if part of a puzzle word
        for c, char in enumerate(line):
            if solution and solution[r][c] == "•":
                line_chars.append(f"{Style.DIM}{char}{Style.RESET_ALL}")
            else:
                line_chars.append(f"{char}")
        output.append(line_chars)
    return output


def make_header(puzzle: Puzzle, text: str) -> str:
    """Generate a header that fits the current puzzle.

    Args:
        puzzle (Puzzle): The current puzzle state.
        text (str): The text to include in the header.

    Returns:
        str: Formatted header.
    """
    hr = "-" * (len(puzzle) * 2 - 1)
    padding = " " * ((len(hr) - len(text)) // 2)
    return f"""{hr}
{padding}{text}{padding}
{hr}"""


def stringify(puzzle: Puzzle) -> str:
    """Convert puzzle array of nested lists into a string.

    Args:
        puzzle (Puzzle): The current puzzle state.

    Returns:
        str: The current puzzle as a string.
    """
    output = []
    for line in puzzle:
        output.append(" ".join(line))
    return "\n".join(output)


def replace_right(
    string: str, target: str, replacement: str, replacements: int = 1
) -> str:
    """Replace `target` with `replacement` from the right size of the string."""
    return replacement.join(string.rsplit(target, replacements))


def get_level_dirs_str(level: int) -> str:
    """Return all pozzible directions for specified level."""
    return replace_right(", ".join(config.level_dirs[level]), ", ", ", and ")


def get_word_list_str(key: Key) -> str:
    """Return all placed puzzle words as a list."""
    return ", ".join([k for k in sorted(key.keys())])


def get_answer_key_str(key: Key) -> str:
    """Return a easy to read answer key for display/export."""
    keys = []
    for k in sorted(key.keys()):
        direction = key[k]["direction"]
        raw_coords: tuple[int, int] = key[k]["start"]
        coords = (raw_coords[0] + 1, raw_coords[1] + 1)
        keys.append(f"{k} {direction} @ {coords}")
    return ", ".join(keys)


def get_random_words(n: int) -> str:
    basedir = Path(__file__).parent
    f = basedir.joinpath("words.txt")
    WORD_LIST = open(f).readlines()
    return ",".join(random.sample(WORD_LIST, n))
