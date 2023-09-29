try:
    from textual import on
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal
    from textual.reactive import reactive
    from textual.widgets import Footer, Header
except ImportError:
    raise ImportError(
        "Please install word-search-generator[play] to use the TUI play interface."
    )

from ... import WordSearch
from ._board import Board
from ._board_cell import BoardCell
from ._puzzle_word import PuzzleWord
from ._screen_quit import QuitScreen
from ._timer import Timer
from ._word_list import WordList
from ._words_to_find import WordsToFind

# TODO: keep score?
# TODO: help screen


class InvalidGameType(Exception):
    """For when a `Game` type hasn't been implemented for TUI play."""

    def __init__(
        self,
        message="Invalid game type. Only WordSearch games at this time.",
    ):
        self.message = message
        super().__init__(self.message)


class TUIGame(App[int]):  # type: ignore[type-arg]
    """A Textual (TUI) application for a Word Search game."""

    CSS_PATH = "style.tcss"
    TITLE = "WORD SEARCH"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("t", "toggle_cheat", "Toggle Cheat Mode"),
        Binding("h", "help", "Help"),
    ]

    cheat_mode = reactive(False)
    found_words = reactive(0)

    def __init__(self, game: WordSearch, *args, **kwargs) -> None:
        """Create an instance of the app.

        Args:
            game (WordSearch): WordSearch to generate puzzle from.
        """
        if not isinstance(game, WordSearch):
            raise InvalidGameType()
        super().__init__(*args, **kwargs)
        self.game = game

    def compose(self) -> ComposeResult:
        """Yield child widgets for the app."""
        yield Header()
        with Horizontal(id="info-bar"):
            yield WordsToFind()
            yield Timer()
        with Horizontal():
            yield WordList(self.game.placed_words)
            yield Board(self.game.puzzle, self.game.bounding_box)
        yield Footer()

    def on_ready(self) -> None:
        self.query_one(WordsToFind).count = len(self.game.placed_words)

    def action_quit(self) -> None:  # type: ignore
        self.push_screen(QuitScreen())

    def action_toggle_cheat(self) -> None:
        """Highlight placed puzzle words."""
        word_list = self.query_one(WordList)
        self.cheat_mode = not self.cheat_mode
        toggled = set()
        for puzzle_word in word_list.unfound_words:
            for cell in puzzle_word.unfound_cells:
                if "correct" not in cell.classes and cell not in toggled:
                    cell.toggle_class("cheat")
                    toggled.add(cell)

    def watch_found_words(self, count: int) -> None:
        self.query_one(WordsToFind).count = len(self.game.placed_words) - count
        if count == len(self.game.placed_words):
            et = self.query_one(Timer)
            et.stop = True
            self.push_screen(
                QuitScreen(
                    f"🥳 Congratulations, you found every word! \n\n{et.renderable}"
                )
            )

    @on(BoardCell.CellClicked)
    def validate_clicked_cell(self, event: BoardCell.CellClicked) -> None:
        word_list = self.app.query_one(WordList)
        for word in word_list.puzzle_words:
            if event.cell in word.cells:
                event.cell.correct = True
                if word.check_found():
                    word.found = True

    @on(PuzzleWord.WordFound)
    def puzzle_word_found(self) -> None:
        self.found_words += 1
