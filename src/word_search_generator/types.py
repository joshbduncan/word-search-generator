from pathlib import Path
from typing import Optional, TypedDict, Union


class KeyInfo(TypedDict):
    start: tuple[int, int]
    direction: str


Puzzle = list[list[str]]
Key = dict[str, KeyInfo]
Fit = Optional[tuple[str, list[tuple[int, int]]]]
Fits = dict[str, list[tuple[int, int]]]
FilePath = Union[str, Path]
