import pathlib

from typing import Dict, List, Optional, Tuple, TypedDict, Union


class KeyInfo(TypedDict):
    start: Tuple[int, int]
    direction: str


Puzzle = List[List[str]]
Key = Dict[str, KeyInfo]
Fit = Optional[Tuple[str, List[Tuple[int, int]]]]
Fits = Dict[str, List[Tuple[int, int]]]
SavePath = Union[str, pathlib.Path, None]
