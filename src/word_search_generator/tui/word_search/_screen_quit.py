from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuitScreen(ModalScreen):  # type: ignore[type-arg]
    """Screen with a dialog to confirm app quit."""

    DEFAULT_MESSAGE = "Are you sure you want to quit?"

    def __init__(self, message: str | None = None) -> None:
        """Create an instance of the modal screen.

        Args:
            message (str | None, optional): Message to display within the modal.
            Defaults to None.
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

    @on(Button.Pressed, "#quit")
    def quit_app(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#cancel")
    def cancel_modal(self) -> None:
        self.app.pop_screen()
