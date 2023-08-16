from __future__ import annotations

from typing import TYPE_CHECKING

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.events import Click


class BoardCell(Static):
    """A cell within a puzzle board grid layout."""

    class CellClicked(Message):
        """Sent when a board cell is clicked."""

        def __init__(self, cell: BoardCell) -> None:
            self.cell = cell
            super().__init__()

    correct = reactive(False)

    def __init__(
        self, character: str, coordinates: tuple[int, int], *args, **kwargs
    ) -> None:
        """Create a board cell instance.

        Args:
            character (str): Alphabet character from puzzle.
            coordinates (tuple[int, int]): Cell position (x, y) within puzzle.
        """
        self.character = character
        self.coordinates = coordinates
        super().__init__(self.character, *args, **kwargs)

    def on_click(self, event: Click) -> None:
        if self.correct:
            return
        self.post_message(self.CellClicked(self))

    def watch_correct(self, val: bool) -> None:
        if not val:
            return
        self.add_class("correct")
