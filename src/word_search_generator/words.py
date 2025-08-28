"""Word list loading and management module.

This module automatically loads word lists from text files in the data directory.
Each .txt file becomes a themed word list accessible via the WORD_LISTS dictionary,
where the key is the filename stem and the value is a list of words.

The word lists are validated to ensure they contain actual words (non-empty,
alphabetic strings) and any invalid entries are filtered out.
"""

import sys
from importlib.resources import files
from pathlib import PurePath

data_dir = files("word_search_generator").joinpath("data")

WORD_LISTS: dict[str, list[str]] = {}


def _is_valid_word(word: str) -> bool:
    """Check if a string is a valid word.

    Args:
        word: String to validate.

    Returns:
        True if word is non-empty and contains only alphabetic characters.
    """
    return bool(word.strip()) and word.strip().isalpha()


def _load_word_list(file_path, name: str) -> list[str]:
    """Load and validate words from a text file.

    Args:
        file_path: Path to the word list file.
        name: Name of the word list for error reporting.

    Returns:
        List of validated words.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        words = [word.strip() for word in content.splitlines() if word.strip()]
        valid_words = [word for word in words if _is_valid_word(word)]

        if not valid_words:
            print(
                f"Warning: No valid words found in word list '{name}'", file=sys.stderr
            )
        elif len(valid_words) != len(words):
            invalid_count = len(words) - len(valid_words)
            print(
                f"Warning: Filtered {invalid_count} invalid entries "
                + f"from word list '{name}'",
                file=sys.stderr,
            )

        return valid_words

    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading word list '{name}': {e}", file=sys.stderr)
        return []


for entry in data_dir.iterdir():
    if entry.is_file() and entry.name.endswith(".txt"):
        stem = PurePath(entry.name).stem
        words = _load_word_list(entry, stem)
        if words:  # Only add non-empty word lists
            WORD_LISTS[stem] = words
