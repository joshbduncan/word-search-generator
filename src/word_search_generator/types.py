from typing import NamedTuple, Optional, TypedDict

from word_search_generator.config import Direction


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
