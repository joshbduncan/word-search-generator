from typing import Generator

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive

from ...word import Word
from ._puzzle_word import PuzzleWord


class WordList(VerticalScroll):
    """List of puzzle words."""

    found_words = reactive(0)
    puzzle_words: set[PuzzleWord] = set()

    def __init__(self, words: set[Word], *args, **kwargs) -> None:
        """Create a word list instance.

        Args:
            words (set[Word]): Game words to include in the list.
        """
        super().__init__(*args, **kwargs)
        self.words = words
        self.border_title = "WORD LIST"

    def compose(self) -> ComposeResult:
        for word in sorted(self.words, key=lambda word: word.text):
            puzzle_word = PuzzleWord(word)
            self.puzzle_words.add(puzzle_word)
            yield puzzle_word

    @property
    def unfound_words(self) -> Generator[PuzzleWord, None, None]:
        return (word for word in self.puzzle_words if not word.found)
