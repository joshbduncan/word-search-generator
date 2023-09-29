from typing import Generator

from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ...word import Word
from ._board import Board


class PuzzleWord(Static):
    """A word for the puzzle word list."""

    class WordFound(Message):
        """Sent when a word is found."""

    found = reactive(False)
    cells: set[Widget] = set()

    def __init__(self, word: Word, *args, **kwargs) -> None:
        """Create a word list word.

        Args:
            word (Word): A WordSearch puzzle word.
        """
        self.word = word
        str = "*" * len(self.word.text) if self.word.secret else self.word.text
        super().__init__(str, *args, **kwargs)

    def on_mount(self) -> None:
        board = self.app.query_one(Board)
        self.cells = board.word_cells(self.word)

    @property
    def unfound_cells(self) -> Generator[Widget, None, None]:
        return (cell for cell in self.cells if not cell.correct)  # type: ignore[attr-defined]  # noqa: E501

    def check_found(self) -> bool:
        """Check if every BoardCell linked to this word is marked correct."""
        return all(cell.correct for cell in self.cells)  # type: ignore[attr-defined]

    def watch_found(self, val: bool) -> None:
        if not val:
            return
        self.add_class("found")
        self.app.bell()
        self.post_message(self.WordFound())
