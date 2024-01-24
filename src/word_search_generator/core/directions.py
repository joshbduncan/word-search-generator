from enum import Enum, unique


@unique
class Direction(Enum):
    """
    If you want custom directions, like `"skipE": (0, 2)`, this is the
    place to monkey-patch them in.

    Tuples are listed in (∂row, ∂col) pairs, presumably b/c that makes
    it easier to use with the Puzzle = list[list[chr]] format
    """

    # is there a better way to specify typing here?
    # without hints here, the linter gets upset with my definitions of r/c_move
    N: tuple[int, int] = (-1, 0)  # type: ignore
    NE: tuple[int, int] = (-1, 1)  # type: ignore
    E: tuple[int, int] = (0, 1)  # type: ignore
    SE: tuple[int, int] = (1, 1)  # type: ignore
    S: tuple[int, int] = (1, 0)  # type: ignore
    SW: tuple[int, int] = (1, -1)  # type: ignore
    W: tuple[int, int] = (0, -1)  # type: ignore
    NW: tuple[int, int] = (-1, -1)  # type: ignore

    @property
    def r_move(self) -> int:
        return self.value[0]

    @property
    def c_move(self) -> int:
        return self.value[1]


# puzzle difficulty levels
LEVEL_DIRS: dict[int, set[Direction]] = {
    -1: set(),  # no valid directions
    1: {  # right or down
        Direction.E,
        Direction.S,
    },
    2: {  # right-facing or down
        Direction.NE,
        Direction.E,
        Direction.SE,
        Direction.S,
    },
    3: {  # any direction
        Direction.N,
        Direction.NE,
        Direction.E,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    4: {  # no E or S for better hiding
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    5: {  # no E
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    7: {  # diagonals only
        Direction.NE,
        Direction.SE,
        Direction.NW,
        Direction.SW,
    },
    8: {  # no diagonals
        Direction.N,
        Direction.E,
        Direction.W,
        Direction.S,
    },
}
