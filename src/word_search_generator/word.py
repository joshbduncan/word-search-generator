from __future__ import annotations

import sys
from enum import Enum, unique
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict  # pragma: no cover


Fit = Optional[Tuple[str, List[Tuple[int, int]]]]
Fits = Dict[str, List[Tuple[int, int]]]


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
    N: Tuple[int, int] = (-1, 0)
    NE: Tuple[int, int] = (-1, 1)
    E: Tuple[int, int] = (0, 1)
    SE: Tuple[int, int] = (1, 1)
    S: Tuple[int, int] = (1, 0)
    SW: Tuple[int, int] = (1, -1)
    W: Tuple[int, int] = (0, -1)
    NW: Tuple[int, int] = (-1, -1)

    @property
    def r_move(self) -> int:
        return self.value[0]

    @property
    def c_move(self) -> int:
        return self.value[1]


class Position(NamedTuple):
    row: Optional[int]
    column: Optional[int]


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
        secret: bool = False,
    ) -> None:
        self.text = text.upper()
        self.start_row: Optional[int] = None
        self.start_column: Optional[int] = None
        self.coordinates: List[Tuple[int, int]] = []
        self.direction: Optional[Direction] = None
        self.secret = secret

    @property
    def placed(self) -> bool:
        # used `is not None` since 0 vals for start_row/column are not truthy
        return all(
            (
                self.start_column is not None,
                self.start_row is not None,
                self.direction is not None,
            )
        )

    @property
    def position(self) -> Position:
        return Position(self.start_row, self.start_column)

    @position.setter
    def position(self, val: Position) -> None:
        self.start_row = val.row
        self.start_column = val.column

    @property
    def position_xy(self) -> Union[str, None]:
        """Returns a string representation of self with 1-based indexing
        and a familiar (x, y) coordinate system"""
        if isinstance(self.start_row, int) and isinstance(self.start_column, int):
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

    def key_string(
        self, bbox: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> Union[str, None]:
        if isinstance(self.start_row, int) and isinstance(self.start_column, int):
            return (
                f"{'*' if self.secret else ''}{self.text} "
                + f"{self.direction.name if self.direction else self.direction}"
                + f" @ {(self.offset_position_xy(bbox))}"
            )
        return None

    def offset_position_xy(
        self, bbox: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> Union[Tuple[int, int], None]:
        if isinstance(self.start_row, int) and isinstance(self.start_column, int):
            offset_start_row = self.start_row + 1 - bbox[0][1]
            offset_start_column = self.start_column + 1 - bbox[0][0]
            return (offset_start_column, offset_start_row)
        return None

    def offset_coordinates(
        self, bbox: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> Union[List[Tuple[int, int]], None]:
        return [(x - bbox[0][0], y - bbox[0][1]) for x, y in self.coordinates]

    def remove_from_puzzle(self):
        """Remove word placement details when a puzzle is reset."""
        self.start_row = None
        self.start_column = None
        self.coordinates = []
        self.direction = None

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Word):
            return False
        return self.text == __o.text

    def __hash__(self) -> int:
        return hash(self.text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.text}', " + f"{self.secret})"

    def __str__(self) -> str:
        return self.text


Wordlist = Union[Set[Word], Any]
