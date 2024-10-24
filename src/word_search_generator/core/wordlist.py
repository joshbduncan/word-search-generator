from collections.abc import Iterable

from .word import Word


class WordList(list[Word]):
    """This class represents a WordList within a WordGame."""

    def __init__(self, words: Iterable[Word], allow_dupes: bool = False) -> None:
        self._allow_dupes = allow_dupes

        _words: list[Word] = []
        for word in words:
            self.validate_word(word)
            if not self._allow_dupes and word in _words:
                continue
            _words.append(word)
        super().__init__(_words)

    def validate_word(self, word, check_for_dupes: bool = False) -> None:
        if not isinstance(word, Word):
            raise TypeError(f"'{word}' must be a 'Word' object.")
        if check_for_dupes and not self._allow_dupes and word in self:
            raise ValueError(f"'{word}' already exists in the WordList.")

    def __setitem__(self, index, word):
        self.validate_word(word, check_for_dupes=True)
        super().__setitem__(index, word)

    def insert(self, index, word):
        self.validate_word(word, check_for_dupes=True)
        super().insert(index, word)

    def append(self, word):
        self.validate_word(word, check_for_dupes=True)
        super().append(word)

    def extend(self, other):
        _words: list[Word] = []
        for word in other:
            # should probably just continue or notify, only raising exception during dev
            self.validate_word(word, check_for_dupes=True)
            _words.append(word)
        super().extend(_words)
