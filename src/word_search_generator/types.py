from enum import Enum, unique
from typing import NamedTuple, Optional, TypedDict


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
    N: tuple[int, int] = (-1, 0)
    NE: tuple[int, int] = (-1, 1)
    E: tuple[int, int] = (0, 1)
    SE: tuple[int, int] = (1, 1)
    S: tuple[int, int] = (1, 0)
    SW: tuple[int, int] = (1, -1)
    W: tuple[int, int] = (0, -1)
    NW: tuple[int, int] = (-1, -1)

    @property
    def r_move(self) -> int:
        return self.value[0]

    @property
    def c_move(self) -> int:
        return self.value[1]


class Position(NamedTuple):
    row: int
    column: int

    @property
    def xy_str(self) -> str:
        """Returns a string representation of self with 1-based indexing
        and a familiar (x, y) coordinate system"""
        return f"({self.column + 1}, {self.row + 1})"


class KeyInfo(TypedDict):
    start: Position
    direction: str
    secret: bool


class KeyInfoJson(TypedDict):
    start_row: int
    start_col: int
    direction: str
    secret: bool


Puzzle = list[list[str]]
Key = dict[str, KeyInfo]
KeyJson = dict[str, KeyInfoJson]
Fit = Optional[tuple[str, list[tuple[int, int]]]]
Fits = dict[str, list[tuple[int, int]]]
DirectionSet = set[Direction]
Wordlist = set[str]
