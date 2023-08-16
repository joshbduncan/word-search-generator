from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuitScreen(ModalScreen):  # type: ignore[type-arg]
    """Screen with a dialog to confirm app quit."""

    DEFAULT_MESSAGE = "Are you sure you want to quit?"

    def __init__(self, message: str | None = None) -> None:
        """Create an instance of the screen.

        Args:
            game (WordSearch): _description_
        """
        super().__init__()
        self.message = message if message else self.DEFAULT_MESSAGE

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
