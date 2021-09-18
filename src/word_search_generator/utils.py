import string

from typing import Dict, List, Set, Tuple
from word_search_generator import config
from word_search_generator.types import Key, Puzzle


def cleanup_input(words: str) -> Set[str]:
    """Cleanup provided input string. Removing spaces
    one-letter words, and words with punctuation.

    Args:
        words (str): String of words separated by commas, spaces, or new lines.

    Raises:
        TypeError: A string was not provided.
        ValueError: No proper words were provided.

    Returns:
        Set[str]: Words to be placed in the puzzle.
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
    word_set: Set[str] = set()
    for word in word_list:
        if len(word_set) > config.max_puzzle_words:
            break
        if len(word) > 1 and not contains_punctuation(word):
            word_set.add(word.upper())
    # if no words were left raise exception
    if not word_set:
        raise ValueError("Use words longer than one-character and without punctuation.")
    return word_set


def contains_punctuation(word):
    """Check to see if puncuation is present in the provided string."""
    return any([True if c in string.punctuation else False for c in word])


def stringify(puzzle: Puzzle, tabs: bool = False) -> str:
    """Convert nested lists into a string separated by either spaces or tabs.

    Args:
        puzzle (Puzzle): he current puzzle state.
        tabs (bool, optional): Use tabs between characters. Defaults to False.

    Returns:
        [str]: The current puzzle as a string.
    """
    string = ""
    spacer = "\t" if tabs else " "
    for line in puzzle:
        string += spacer.join(line) + "\n"
    return string.strip("\n")


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
        raw_coords: Tuple[int, int] = key[k]["start"]
        coords = (raw_coords[0] + 1, raw_coords[1] + 1)
        keys.append(f"{k} {direction} @ {coords}")
    return ", ".join(keys)
