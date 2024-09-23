from word_search_generator.core import Game, Word
from word_search_generator.core.directions import NDS
from word_search_generator.core.game import WordSet


class Crossword(Game):
    def __init__(self, text: str, preprocessed_words: WordSet | None = None):
        words: WordSet = (
            preprocessed_words if preprocessed_words else set()
        ) | self._process_input(text)

        super().__init__(words, 1)

    def _process_input(self, text: str, *_) -> WordSet:
        """
        Tab-separated rows with one line per word

        Word\tDescription\t<optional int>priority\t\t\t(ignored stuff)\t\t
        """
        o = set()
        for line in text.splitlines():
            w, d, *p = line.split("\t")
            o.add(Word(w, False, NDS.CROSSWORD, int(p[0]) if p else 3, d))
        return o
