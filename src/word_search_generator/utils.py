from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, TypeAlias

from .words import WORD_LISTS

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    from .core.game import DirectionSet, Puzzle, Word, WordSet


BoundingBox: TypeAlias = tuple[tuple[int, int], tuple[int, int]]


def round_half_up(n: float, decimals: int = 0) -> float:
    """Round numbers in a consistent and familiar format.

    Uses the "round half up" strategy where 0.5 always rounds up to 1.

    Args:
        n: The number to round.
        decimals: Number of decimal places to round to. Defaults to 0.

    Returns:
        The rounded number.
    """
    multiplier: int = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def float_range(
    start: int | float,
    stop: int | float | None = None,
    step: int | float | None = None,
) -> Iterator[float]:
    """Generate a float-based range for iteration.

    Similar to range() but works with floating point numbers.

    Args:
        start: Starting value. If stop is None, this becomes the stop value
            and start becomes 0.
        stop: Stopping value (exclusive). Defaults to None.
        step: Step size. Defaults to 1.0.

    Yields:
        Float values from start to stop (exclusive) in increments of step.
    """
    start = float(start)
    if stop is None:
        stop = start + 0.0
        start = 0.0
    if step is None:
        step = 1.0
    count = 0
    while True:
        temp = float(start + count * step)
        if (step > 0 and temp >= stop) or (step < 0 and temp <= stop):
            break
        yield temp
        count += 1


def distance(x: int | float, y: int | float, ratio: float) -> float:
    """Calculate the distance between two coordinates on a grid.

    Args:
        x: X coordinate.
        y: Y coordinate.
        ratio: Aspect ratio multiplier for y coordinate.

    Returns:
        Euclidean distance between the coordinates.
    """
    return math.sqrt(math.pow(y * ratio, 2) + math.pow(x, 2))


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    """Validate position (x, y) is within the supplied bounds.

    Args:
        x: X coordinate to check.
        y: Y coordinate to check.
        width: Maximum width (exclusive).
        height: Maximum height (exclusive).

    Returns:
        True if the position is within bounds, False otherwise.
    """
    return x >= 0 and x < width and y >= 0 and y < height


def find_bounding_box(
    grid: list[list[str]],
    edge: str,
) -> BoundingBox:
    """Find the bounding box of cells matching the edge character.

    Scans the grid once to find the smallest rectangle that contains all
    cells matching the specified edge character.

    Args:
        grid: 2D grid of strings to search.
        edge: Character to search for in the grid.

    Returns:
        BoundingBox: Tuple of ((min_x, min_y), (max_x, max_y)) coordinates
        representing the top-left and bottom-right corners of the bounding box.
        Returns ((0, 0), (0, 0)) if edge character is not found.
    """
    size = len(grid)
    min_x, min_y = size, size
    max_x, max_y = -1, -1

    # Single pass through the grid
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == edge:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    # Handle case where edge is not found
    if max_x == -1:
        return ((0, 0), (0, 0))

    return ((min_x, min_y), (max_x, max_y))


def stringify(puzzle: Puzzle, bbox: BoundingBox) -> str:
    """Convert puzzle array of nested lists into a string.

    Args:
        puzzle: 2D puzzle grid to stringify.
        bbox: Bounding box defining the area to stringify.

    Returns:
        String representation of the puzzle grid with proper spacing.
    """
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
    """Return possible directions for specified level as a string.

    Args:
        level: Set of Direction objects representing the difficulty level.

    Returns:
        Comma-separated string of direction names with "and" before the last item.
    """
    level_dirs_str = [d.name for d in level]
    level_dirs_str.insert(-1, "and")
    return ", ".join(level_dirs_str)


def get_word_list_str(words: WordSet) -> str:
    """Return all placed puzzle words as a string (excluding secret words).

    Args:
        words: Set of Word objects from the puzzle.

    Returns:
        Comma-separated string of placed word texts.
    """
    return ", ".join(word.text for word in get_word_list_list(words))


def get_word_list_list(words: WordSet) -> list[Word]:
    """Return all placed puzzle words as a list (excluding secret words).

    Args:
        words: Set of Word objects from the puzzle.

    Returns:
        List of Word objects that are placed and not secret.
    """
    return [word for word in words if word.placed and not word.secret]


def get_answer_key_list(
    word_list: list[Word],
    bbox: BoundingBox,
    lowercase: bool = False,
    reversed_letters: bool = False,
) -> list[str]:
    """Return an easy to read answer key for display/export.

    Resulting coordinates will be offset by the supplied values.
    Used for masked puzzles.

    Args:
        word_list: A list of Word objects.
        bbox: Puzzle mask bounding box for coordinate offset.
        lowercase: Should words be lowercase. Defaults to False.
        reversed_letters: Should word letters be reversed. Defaults to False.

    Returns:
        List of placed words with their placement information.
    """
    return [w.key_string(bbox, lowercase, reversed_letters) for w in word_list]


def get_answer_key_str(words: list[Word], bbox: BoundingBox) -> str:
    """Return an easy to read answer key for display.

    Resulting coordinates will be offset by the supplied values.
    Used for masked puzzles.

    Args:
        words: A list of Word objects.
        bbox: Puzzle mask bounding box that coordinates should be offset by.

    Returns:
        Comma-separated string of answer key entries.
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

    Raises:
        ValueError: If n is less than 1, word_list is empty,
            or insufficient words available.
    """
    if n < 1:
        raise ValueError("Number of words must be at least 1")

    if word_list is None:
        word_list = WORD_LISTS["dictionary"]

    if not word_list:
        raise ValueError("Word list is empty - cannot generate random words")

    if max_length is not None:
        word_list = [word for word in word_list if len(word) <= max_length]
        if not word_list:
            raise ValueError(
                f"No words found with length <= {max_length} in the specified word list"
            )

    if len(word_list) < n:
        raise ValueError(
            f"Requested {n} random words but only {len(word_list)} "
            f"are available in the specified word list"
        )

    return ",".join(random.sample(word_list, n))
