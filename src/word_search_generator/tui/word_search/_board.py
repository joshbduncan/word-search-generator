from textual.app import ComposeResult
from textual.containers import Grid
from textual.widget import Widget

from ...game import Puzzle
from ...word import Word
from ._board_cell import BoardCell


class Board(Grid):
    """A puzzle board grid layout."""

    def __init__(
        self,
        puzzle: Puzzle,
        bounding_box: tuple[tuple[int, int], tuple[int, int]],
        *args,
        **kwargs,
    ) -> None:
        """Create a puzzle board.

        Args:
            puzzle (Puzzle): Puzzle to draw board from.
            bounding_box (tuple[tuple[int, int], tuple[int, int]]): Puzzle bounding box.
        """
        super().__init__(*args, **kwargs)
        self.puzzle = puzzle
        self.bounding_box = bounding_box
        self.border_title = "PUZZLE BOARD"
        self.styles.grid_size_columns = (
            self.bounding_box[1][0] - self.bounding_box[0][0] + 1
        )

    def compose(self) -> ComposeResult:
        min_x, min_y = self.bounding_box[0]
        max_x, max_y = self.bounding_box[1]
        for y, row in enumerate(self.puzzle[min_y : max_y + 1]):
            for x, col in enumerate(row[min_x : max_x + 1]):
                yield BoardCell(
                    character=col,
                    coordinates=(x + 1, y + 1),
                    id=f"x{x+1}-y{y+1}",
                )

    def word_cells(self, word: Word) -> set[Widget]:
        return {
            self.get_child_by_id(f"x{x}-y{y}")
            for x, y in word.offset_coordinates(self.bounding_box)
        }
