from __future__ import annotations

from typing import Any, List, Optional

from . import config
from .utils import build_puzzle, find_bounding_box

PuzzleGrid = List[List[str]]


class Puzzle:
    """This class represents a WordSearch puzzle object."""

    def __init__(self, size: Optional[int] = None) -> None:
        """Initialize a puzzle for a WordSearch game."""
        self._size: int = size if size else 0
        self._puzzle: PuzzleGrid = (
            build_puzzle(self._size, config.ACTIVE) if size else []
        )
        self._masks: List[Any] = []

    @property
    def puzzle(self) -> PuzzleGrid:
        """The current puzzle state."""
        return self._puzzle

    @property
    def is_masked(self) -> bool:
        """Puzzle masking status."""
        return bool(self.masks)

    def show(self) -> None:
        """Show the full puzzle grid."""
        for r in self.puzzle:
            print(" ".join(r))

    def show_cropped(self) -> None:
        """Show puzzle grid cropped to the active bounding box."""
        top_edge, left_edge, right_edge, bottom_edge = find_bounding_box(self.puzzle)
        for r in self.puzzle[top_edge:bottom_edge]:
            print(" ".join(r[left_edge:right_edge]))

    def _reset_puzzle(self) -> None:
        """Reset and regenerate the puzzle."""
        self._puzzle = build_puzzle(self._size, config.ACTIVE)
        # self._reapply_masks()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._size})"
