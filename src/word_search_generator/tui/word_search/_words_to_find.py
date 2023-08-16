from textual.reactive import reactive
from textual.widgets import Static


class WordsToFind(Static):
    """A widget to display the remaining words to be found in the puzzle."""

    count = reactive(0)

    def render(self) -> str:
        return f"WORDS TO FIND {self.count}"
