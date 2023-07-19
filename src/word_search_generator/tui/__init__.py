from time import monotonic
from typing import Generator

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Grid, Horizontal, VerticalScroll
    from textual.events import Click
    from textual.reactive import reactive
    from textual.screen import ModalScreen
    from textual.widget import Widget
    from textual.widgets import Button, Footer, Header, Label, Static
except ImportError:
    raise ImportError(
        "Please install word-search-generator[play] to use the TUI play interface."
    )

from .. import WordSearch
from ..word import Position, Word

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


class QuitScreen(ModalScreen):  # type: ignore[type-arg]
    """Screen with a dialog to confirm app quit."""

    DEFAULT_MESSAGE = "Are you sure you want to quit?"

    def __init__(self, message: str | None = None) -> None:
        """Create an instance of the screen.

        Args:
            game (WordSearch): _description_
        """
        self.message = message if message else self.DEFAULT_MESSAGE
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.message, id="message"),
            Button("Quit", variant="primary", id="quit"),
            Button("Cancel", variant="default", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()


class WordsToFind(Static):
    """A widget to display the remaining words to be found in the puzzle."""

    count = reactive(0)

    def render(self) -> str:
        return f"WORDS TO FIND {self.count}"


class ElapsedTime(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)  # type: ignore
    time = reactive(0.0)

    def on_mount(self) -> None:
        """Set event handler for updating the time."""
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        """Update the time to the current time."""
        self.time = monotonic() - self.start_time  # type: ignore[operator]

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"Elapsed Time: {hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")


class PuzzleWord(Static):
    """A word for the puzzle word list."""

    found = reactive(False)

    def __init__(self, word: Word, *args, **kwargs) -> None:
        """Create a word list word instance.

        Args:
            word (Word): A WordSearch puzzle word.
        """
        self.word = word
        self._found: bool = False
        str = "*" * len(self.word.text) if self.word.secret else self.word.text
        super().__init__(str, *args, **kwargs)

    def check_if_found(self) -> None:
        """Check if all word characters have been found."""
        if not self.cells:
            return
        if all(cell.correct for cell in self.cells):  # type: ignore[attr-defined]
            self.found = True

    @property
    def cells(self) -> Generator[Widget, None, None] | None:
        """All BoardCells that make up this word in the puzzle."""
        board = self.app.get_widget_by_id("board")
        bbox = self.app.game.bounding_box  # type: ignore[attr-defined]
        offset_coordinates: list[Position] | None = self.word.offset_coordinates(bbox)
        if not offset_coordinates:  # only here for mypy
            return None
        return (board.get_child_by_id(f"x{x}-y{y}") for x, y in offset_coordinates)

    def watch_found(self, val: bool) -> None:
        if not val:
            return
        self.app.bell()
        self.add_class("found")
        self.app.found_words += 1  # type: ignore[attr-defined]
        if self.word.direction is None:  # only here for mypy
            return
        msg = f"'{self.word.text}' successfully found going {self.word.direction.name}!"
        self.log.debug(msg)


class BoardCell(Static):
    """A cell within a puzzle board grid layout."""

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
        self._correct: bool = False
        super().__init__(self.character, *args, **kwargs)

    def on_click(self, event: Click) -> None:
        msg = f"Clicked on '{self.character}' @ {self.coordinates}."
        self.log.debug(msg)
        self.check_cell()

    def check_cell(self) -> None:
        if self.correct:
            return
        word_list = self.app.get_widget_by_id("word-list")
        for puzzle_word in word_list.children:
            if self in puzzle_word.cells:  # type: ignore[attr-defined]
                self.correct = True
            puzzle_word.check_if_found()  # type: ignore[attr-defined]

    def watch_correct(self, val: bool) -> None:
        if not val:
            return
        self.add_class("correct")
        msg = f"'{self.character}' correctly selected!"
        self.log.debug(msg)


class TUIGame(App):  # type: ignore[type-arg]
    """A Textual (TUI) application for a Word Search game."""

    CSS_PATH = "style.css"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+t", "toggle_cheat", "Toggle Cheat Mode"),
        Binding("ctrl+h", "help", "Help"),
    ]

    cheat_mode = False
    found_words = reactive(0)

    def __init__(self, game: WordSearch, *args, **kwargs) -> None:
        """Create an instance of the app.

        Args:
            game (WordSearch): WordSearch to generate puzzle from.
        """
        if not isinstance(game, WordSearch):
            raise InvalidGameType()
        self.game = game
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Yield child widgets for the app."""
        yield Header()
        self.title = "WORD SEARCH"
        with Horizontal(id="info-bar"):
            yield WordsToFind()
            yield ElapsedTime("Elapsed Time: 00:00:00.00")
        with Horizontal():
            with VerticalScroll(id="word-list"):
                words = sorted(self.game.placed_words, key=lambda word: word.text)
                for word in words:
                    yield PuzzleWord(word, classes="word")
            with Grid(id="board"):
                min_x, min_y = self.game.bounding_box[0]
                max_x, max_y = self.game.bounding_box[1]
                for y, row in enumerate(self.game.puzzle[min_y : max_y + 1]):
                    for x, col in enumerate(row[min_x : max_x + 1]):
                        yield BoardCell(
                            character=col,
                            coordinates=(x + 1, y + 1),
                            id=f"x{x+1}-y{y+1}",
                            classes="cell",
                        )
        yield Footer()

    def on_mount(self) -> None:
        """Update board and word list when app is mounted."""
        board = self.get_widget_by_id("board")
        board.border_title = "PUZZLE BOARD"
        columns = self.game.bounding_box[1][0] - self.game.bounding_box[0][0] + 1
        board.styles.grid_size_columns = columns
        word_list = self.get_widget_by_id("word-list")
        word_list.border_title = "WORD LIST"

    def action_quit(self) -> None:  # type: ignore
        self.push_screen(QuitScreen())

    def action_toggle_cheat(self) -> None:
        """Highlight placed puzzle words."""
        self.cheat_mode = not self.cheat_mode
        toggled = set()
        msg = "Enabling cheat mode." if self.cheat_mode else "Disabling cheat mode."
        self.log.debug(msg)
        word_list = self.get_widget_by_id("word-list")
        for puzzle_word in word_list.children:
            if puzzle_word.found:  # type: ignore[attr-defined]
                continue
            board = self.get_widget_by_id("board")
            obj = puzzle_word.word  # type: ignore[attr-defined]
            bbox = self.game.bounding_box
            offset_coordinates = obj.offset_coordinates(bbox)
            for x, y in offset_coordinates:
                if (x, y) in toggled:
                    continue
                cell = board.get_child_by_id(f"x{x}-y{y}")
                if "correct" not in cell.classes:
                    cell.toggle_class("cheat")
                    toggled.add((x, y))

    async def watch_found_words(self, count: int) -> None:
        self.query_one(WordsToFind).count = len(self.game.placed_words) - count
        if count == len(self.game.placed_words):
            et = self.query_one(ElapsedTime)
            self.push_screen(
                QuitScreen(
                    f"🥳 Congratulations, you found every word! \n\n{et.renderable}"
                )
            )
