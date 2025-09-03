"""Direction system and difficulty levels for word placement.

This module defines the 8 cardinal and intercardinal directions for placing
words in a puzzle grid, along with predefined difficulty levels that restrict
which directions can be used.

Coordinates use (row_delta, col_delta) format where:
- Negative row values move up (North)
- Positive row values move down (South)
- Negative col values move left (West)
- Positive col values move right (East)
"""

from enum import Enum, unique


@unique
class Direction(Enum):
    """Cardinal and intercardinal directions for word placement.

    Each direction is represented as a (row_delta, col_delta) tuple that
    defines how to move from one grid position to the next when placing
    a word in that direction.

    The coordinate system assumes a 2D grid where:
    - (0, 0) is the top-left corner
    - Row increases downward (South)
    - Column increases rightward (East)

    Custom directions can be added by extending this enum with new
    (row_delta, col_delta) values.
    """

    N = (-1, 0)  # North: move up one row
    NE = (-1, 1)  # Northeast: move up one row, right one column
    E = (0, 1)  # East: move right one column
    SE = (1, 1)  # Southeast: move down one row, right one column
    S = (1, 0)  # South: move down one row
    SW = (1, -1)  # Southwest: move down one row, left one column
    W = (0, -1)  # West: move left one column
    NW = (-1, -1)  # Northwest: move up one row, left one column

    @property
    def r_move(self) -> int:
        """Get the row movement delta for this direction.

        Returns:
            The row offset (-1 for up, 0 for no change, 1 for down).
        """
        return self.value[0]

    @property
    def c_move(self) -> int:
        """Get the column movement delta for this direction.

        Returns:
            The column offset (-1 for left, 0 for no change, 1 for right).
        """
        return self.value[1]


"""Difficulty level mappings for word placement directions.

Each level restricts which directions words can be placed in, with higher
numbers generally being more difficult (except for specialized levels 7-8):

- Level -1: Invalid/testing level (no directions)
- Level 1: Beginner (right and down only)
- Level 2: Easy (right-facing directions and down)
- Level 3: Normal (all 8 directions)
- Level 4: Hard (excludes easiest directions)
- Level 5: Expert (excludes horizontal right)
- Level 6: Master (backward-facing directions only)
- Level 7: Challenge (diagonals only)
- Level 8: Orthogonal (no diagonals)
"""
LEVEL_DIRS: dict[int, set[Direction]] = {
    -1: set(),  # Invalid level: no valid directions (used for testing/validation)
    1: {  # Beginner: horizontal right and vertical down only
        Direction.E,
        Direction.S,
    },
    2: {  # Easy: right-facing directions and vertical down
        Direction.NE,
        Direction.E,
        Direction.SE,
        Direction.S,
    },
    3: {  # Normal: all 8 directions allowed
        Direction.N,
        Direction.NE,
        Direction.E,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    4: {  # Hard: all directions except the easiest (E and S)
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    5: {  # Expert: all directions except horizontal right
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    6: {  # Master: backward-facing directions only
        Direction.NW,
        Direction.W,
        Direction.SW,
    },
    7: {  # Challenge: diagonal directions only
        Direction.NE,
        Direction.SE,
        Direction.SW,
        Direction.NW,
    },
    8: {  # Orthogonal: cardinal directions only (no diagonals)
        Direction.N,
        Direction.E,
        Direction.S,
        Direction.W,
    },
}
