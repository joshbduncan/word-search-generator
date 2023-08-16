from __future__ import annotations

import math
import random
from math import log2
from typing import TYPE_CHECKING, Any, Sized

from . import config
from .words import WORD_LIST

if TYPE_CHECKING:  # pragma: no cover
    from .game import DirectionSet, Key, Puzzle
    from .word import WordSet


def calc_puzzle_size(words: WordSet, level: Sized, size: int | None = None) -> int:
    """Calculate the puzzle grid size."""
    all_words = [word.text for word in words]
    longest_word_length = len(max(all_words, key=len))
    if not size:
        longest = max(10, longest_word_length)
        # calculate multiplier for larger word lists so that most have room to fit
        multiplier = len(all_words) / 15 if len(all_words) > 15 else 1
        # level lengths in config.py are nice multiples of 2
        l_size = log2(len(level)) if level else 1  # protect against log(0) in tests
        size = min(round(longest + l_size * 2 * multiplier), config.max_puzzle_size)
    return size


def build_puzzle(size: int, char: str) -> Puzzle:
    return [[char] * size for _ in range(size)]


def round_half_up(n: float, decimals: int = 0) -> float | Any:  # mypy 0.95+ weirdness
    """Round numbers in a consistent and familiar format."""
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def float_range(
    start: int | float,
    stop: int | float | None = None,
    step: int | float | None = None,
):
    """Generate a float-based range for iteration."""
    start = float(start)
    if stop is None:
        stop = start + 0.0
        start = 0.0
    if step is None:
        step = 1.0
    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop or step < 0 and temp <= stop:
            break
        yield temp
        count += 1


def distance(x: int, y: int, ratio: float) -> float:
    """Calculate the distance between two coordinates on a grid."""
    return math.sqrt(math.pow(y * ratio, 2) + math.pow(x, 2))


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    """Validate position (x, y) is within the supplied bounds."""
    return x >= 0 and x < width and y >= 0 and y < height


def find_bounding_box(
    grid: list[list[str]], edge: str = config.ACTIVE
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Bounding box of the masked area as a rectangle defined
    by a tuple of (top-left edge as x, y, bottom-right edge as x, y)"""
    size = len(grid)
    min_y = 0
    for i, r in enumerate(grid):
        if edge in r:
            min_y = i
            break
    max_y = size
    for i, r in enumerate(reversed(grid)):
        if edge in r:
            max_y = size - 1 - i
            break
    cols = [list(c) for c in zip(*grid)]  # mypy not playing nice w/ `list(zip(*grid))``
    min_x = 0
    for i, r in enumerate(cols):
        if edge in r:
            min_x = i
            break
    max_x = size
    for i, r in enumerate(reversed(cols)):
        if edge in r:
            max_x = size - 1 - i
            break
    return ((min_x, min_y), (max_x, max_y))


def direction_set_repr(ds: DirectionSet) -> str:
    return ("'" + ",".join(d.name for d in ds) + "'") if ds else "None"


def stringify(puzzle: Puzzle, bbox: tuple[tuple[int, int], tuple[int, int]]) -> str:
    """Convert puzzle array of nested lists into a string."""
    min_x, min_y = bbox[0]
    max_x, max_y = bbox[1]
    output = []
    offset = " " if max_x - min_x < 5 else ""
    for line in puzzle[min_y : max_y + 1]:
        output.append(
            offset + " ".join([c if c else " " for c in line[min_x : max_x + 1]])
        )
    return "\n".join(output)


def get_level_dirs_str(level: DirectionSet) -> str:
    """Return possible directions for specified level as a string."""
    level_dirs_str = [d.name for d in level]
    level_dirs_str.insert(-1, "and")
    return ", ".join(level_dirs_str)


def get_word_list_str(key: Key) -> str:
    """Return all placed puzzle words as a list (excluding secret words)."""
    return ", ".join(get_word_list_list(key))


def get_word_list_list(key: Key) -> list[str]:
    """Return all placed puzzle words as a list (excluding secret words)."""
    return [k for k in sorted(key.keys()) if not key[k]["secret"]]


def get_answer_key_list(
    words: WordSet, bbox: tuple[tuple[int, int], tuple[int, int]]
) -> list[str]:
    """Return a easy to read answer key for display/export. Resulting coordinates
    will be offset by the supplied values. Used for masked puzzles.

    Args:
        words (WordSet): A list of `Word` objects.
        bbox (tuple[int, int, int, int]): Puzzle mask bounding box
        coordinates should be offset by.
    """
    return [w.key_string(bbox) for w in sorted(words, key=lambda word: word.text)]


def get_answer_key_str(
    words: WordSet, bbox: tuple[tuple[int, int], tuple[int, int]]
) -> str:
    """Return a easy to read answer key for display. Resulting coordinates
    will be offset by the supplied values. Used for masked puzzles.

    Args:
        words (WordSet): A list of `Word` objects.
        bbox (tuple[int, int, int, int]): Puzzle mask bounding box
        coordinates should be offset by.
    """
    return ", ".join(get_answer_key_list(words, bbox))


def get_random_words(n: int, max_length: int | None = None) -> list[str]:
    """Return a list of random dictionary words."""
    if max_length:
        return random.sample([word for word in WORD_LIST if len(word) <= max_length], n)
    return random.sample(WORD_LIST, n)
