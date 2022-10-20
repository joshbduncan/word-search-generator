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


class KeyInfo(TypedDict):
    start: Optional[Position]
    direction: Optional[Direction]
    secret: bool


class KeyInfoJson(TypedDict):
    start_row: Optional[int]
    start_col: Optional[int]
    direction: Optional[str]
    secret: bool


class Word:
    """This class represents a Word within a WordSearch puzzle."""

    def __init__(
        self,
        text: str,
        start_row: Optional[int] = None,
        start_column: Optional[int] = None,
        direction: Optional[Direction] = None,
        secret: bool = False,
    ):
        self.text = text.upper()
        self._start_row: Optional[int] = start_row
        self._start_column: Optional[int] = start_column
        self.direction: Optional[Direction] = direction
        self.secret = secret

    @property
    def start_row(self) -> int | None:
        if isinstance(self._start_row, int):
            return self._start_row
        return None

    @property
    def start_column(self) -> int | None:
        if isinstance(self._start_column, int):
            return self._start_column
        return None

    @property
    def position(self) -> Position | None:
        if isinstance(self.start_row, int) and isinstance(self.start_column, int):
            return Position(self.start_row, self.start_column)
        return None

    @position.setter
    def position(self, val: Position):
        self._start_row = val.row
        self._start_column = val.column

    @property
    def position_xy(self) -> str | None:
        """Returns a string representation of self with 1-based indexing
        and a familiar (x, y) coordinate system"""
        if self.start_row and self.start_column:
            return f"({self.start_column + 1}, {self.start_row + 1})"
        return None

    @property
    def key_info(self) -> KeyInfo:
        return {
            "start": self.position,
            "direction": self.direction,
            "secret": self.secret,
        }

    @property
    def key_info_json(self) -> KeyInfoJson:
        return {
            "start_row": self.start_row,
            "start_col": self.start_column,
            "direction": self.direction.name if self.direction else None,
            "secret": self.secret,
        }

    @property
    def key_string(self) -> str | None:
        if not self.position:
            return None
        return (
            f"{'*' if self.secret else ''}{self.text} "
            + f"{self.direction.name if self.direction else self.direction}"
            + f" @ {self.position_xy}"
        )

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Word):
            return False
        return self.text == __o.text

    def __hash__(self) -> int:
        return hash(self.text)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}('{self.text}', "
            + f"{self.start_row}, "
            + f"{self.start_column}, "
            + f"{self.direction}, "
            + f"{self.secret})"
        )

    def __str__(self):
        return self.text


Puzzle = list[list[str]]
Key = dict[str, KeyInfo]
KeyJson = dict[str, KeyInfoJson]
Fit = Optional[tuple[str, list[tuple[int, int]]]]
Fits = dict[str, list[tuple[int, int]]]
DirectionSet = set[Direction]
Wordlist = set[Word]
