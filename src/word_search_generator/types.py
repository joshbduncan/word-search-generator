from typing import Any, Dict, List, Tuple, TypedDict


class KeyDict(TypedDict):
    start: Tuple[int, int]
    direction: str


class CompletedPuzzle(TypedDict):
    puzzle: List[List[str]]
    solution: List[List[str]]
    # had to put `Any` below because mypy wouldn't accept KeyDict
    key: Dict[str, Any]
