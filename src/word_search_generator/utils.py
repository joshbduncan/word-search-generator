from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, TypeAlias

from .words import WORD_LISTS

if TYPE_CHECKING:  # pragma: no cover
    from .core.game import DirectionSet, Puzzle, Word, WordSet


BoundingBox: TypeAlias = tuple[tuple[int, int], tuple[int, int]]


def round_half_up(n: float, decimals: int = 0) -> float:
    """Round numbers in a consistent and familiar format."""
    multiplier: int = 10**decimals
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
    grid: list[list[str]],
    edge: str,
) -> BoundingBox:
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
    # mypy not playing nice w/ `list(zip(*grid))`
    cols = [list(c) for c in zip(*grid, strict=False)]
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


def stringify(puzzle: Puzzle, bbox: BoundingBox) -> str:
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


def get_LEVEL_DIRS_str(level: DirectionSet) -> str:
    """Return possible directions for specified level as a string."""
    LEVEL_DIRS_str = [d.name for d in level]
    LEVEL_DIRS_str.insert(-1, "and")
    return ", ".join(LEVEL_DIRS_str)


def get_word_list_str(words: WordSet) -> str:
    """Return all placed puzzle words as a list (excluding secret words)."""
    return ", ".join(word.text for word in get_word_list_list(words))


def get_word_list_list(words: WordSet) -> list[Word]:
    """Return all placed puzzle words as a list (excluding secret words)."""
    return [word for word in words if word.placed and not word.secret]


def get_answer_key_list(
    word_list: list[Word],
    bbox: BoundingBox,
    lowercase: bool = False,
    reversed_letters: bool = False,
) -> list[str]:
    """Return a easy to read answer key for display/export. Resulting coordinates
    will be offset by the supplied values. Used for masked puzzles.

    Args:
        word_list: A list of `Word` objects.
        bbox: Puzzle mask bounding box
        lowercase: Should words be lowercase. Defaults to False.
        reversed_letters: Should words letters be reversed. Defaults to False.

    Returns:
        List of placed words with their placement information.
    """
    return [w.key_string(bbox, lowercase, reversed_letters) for w in word_list]


def get_answer_key_str(words: list[Word], bbox: BoundingBox) -> str:
    """Return a easy to read answer key for display. Resulting coordinates
    will be offset by the supplied values. Used for masked puzzles.

    Args:
        words (WordSet): A list of `Word` objects.
        bbox (tuple[int, int, int, int]): Puzzle mask bounding box
        coordinates should be offset by.
    """
    return ", ".join(get_answer_key_list(words, bbox))


def get_random_words(
    n: int,
    max_length: int | None = None,
    word_list: list[str] | None = None,
) -> str:
    """Return a string of random words separated by a comma.

    Args:
        n: Random words to return
        max_length: Maximum allowed length of any returned word. Defaults to None.
        word_list: List of words to sample from. Defaults to base dictionary.

    Returns:
        A string of random words separated by a comma.
    """
    if word_list is None:
        word_list = WORD_LISTS["dictionary"]

    if max_length is not None:
        word_list = [word for word in word_list if len(word) <= max_length]

    try:
        return ",".join(random.sample(word_list, n))
    except ValueError as e:
        e.add_note(
            f"You requested '{n}' random words but only '{len(word_list)}' \
were available in the specified word list."
        )
        raise
