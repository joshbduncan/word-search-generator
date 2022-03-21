from typing import Optional, TypedDict


class KeyInfo(TypedDict):
    start: tuple[int, int]
    direction: str


class KeyInfoJson(TypedDict):
    start_row: int
    start_col: int
    direction: str


Puzzle = list[list[str]]
Key = dict[str, KeyInfo]
KeyJson = dict[str, KeyInfoJson]
Fit = Optional[tuple[str, list[tuple[int, int]]]]
Fits = dict[str, list[tuple[int, int]]]
