import string

from . import config


def cleanup_input(words: str) -> set:
    """Cleanup provided input string. Removing spaces
    one-letter words, and words with punctuation.

    Args:
        words (str): String of words separated by commas, spaces, or new lines.

    Raises:
        TypeError: A string was not provided.
        ValueError: No proper words were provided.

    Returns:
        set: Words to be placed in the puzzle.
    """
    if type(words) != str:
        raise TypeError(
            "Must be a string of words separated by spaces, commas, or new lines"
        )
    # remove new lines
    words = words.replace("\n", ",")
    # remove excess spaces and commas
    words = ",".join(words.split(" ")).split(",")
    # iterate through all words and pick first set that match criteria
    word_list = set()
    for word in words:
        if len(word_list) >= config.max_puzzle_words:
            break
        if len(word) > 1 and not check_for_punctuation(word):
            word_list.add(word.upper())
    # if no words were left raise exception
    if not word_list:
        raise ValueError(
            "No valid words. Use words that don't have punctuation and are longer than one-character."
        )
    # return words to be placed in the puzzle
    return word_list


def check_for_punctuation(word):
    """Check to see if puncuation is present in the provided string."""
    return any([True if c in string.punctuation else False for c in word])


def stringify(puzzle: list, tabs: bool = False):
    """Convert a list of list into a string separated by either spaces or tabs.

    Args:
        puzzle (list): The current puzzle state.
        tabs (bool, optional): Use tabs between characters.

    Returns:
        [type]: A string with of the current puzzle.
    """
    string = ""
    spacer = "\t" if tabs else " "
    for line in puzzle:
        string += spacer.join(line) + "\n"
    return string.strip("\n")


def replace_right(s: str, target: str, replacement: str, replacements: int = 1) -> str:
    return replacement.join(s.rsplit(target, replacements))


def get_level_dirs_str(level: int) -> str:
    return replace_right(", ".join(config.level_dirs[level]), ", ", ", and ")


def get_word_list_str(key: dict) -> str:
    return ", ".join([k for k in sorted(key.keys())])


def get_answer_key_str(key: dict) -> str:
    return ", ".join(
        [f"{k} {key[k]['dir']} @ {key[k]['start']}" for k in sorted(key.keys())]
    )
