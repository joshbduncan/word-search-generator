#! /usr/bin/env python3

from typing import Literal

from word_search_generator.core import Game, Word
from word_search_generator.core.directions import NDS
from word_search_generator.core.game import WordSet

from ._generator import CrosswordGenerator, CrosswordFromWordSearch
from ..utils import get_random_words
from ..words import WORD_LIST


class Crossword(Game):
    GENERATORS = {
        "cw": CrosswordFromWordSearch,
        "ws": CrosswordGenerator,
    }

    def __init__(
        self,
        text: str,
        preprocessed_words: WordSet | None = None,
        generation_method: Literal["cw", "ws"] = "ws",
    ):
        words: WordSet = (
            preprocessed_words if preprocessed_words else set()
        ) | self._process_input(text)

        super().__init__(
            words,
            1,
            require_all_words=True,
            generator=self.GENERATORS[generation_method],
        )

    def _process_input(self, text: str, *_) -> WordSet:
        """
        Tab-separated rows with one line per word

        Word\tDescription\t<optional int>priority\t\t\t(ignored stuff)\t\t

        Priority < 0 makes the word optional to include
        """
        o = set()
        for line in text.splitlines():
            w, d, *p = line.split("\t")
            p = int(p[0]) if p else 3
            o.add(Word(w, False, NDS.CROSSWORD, p, p >= 0, d))
        return o


RANDOM_CROSSWORD_WORDS = "\n".join(
    [f"{w}\t{w}" for w in get_random_words(50, 9)]
    + [f"{w}\t{w}" for w in get_random_words(20, None, 10)]
)


def demo_crosswords():
    print("Testing WordSearch crossword")
    ws = Crossword(RANDOM_CROSSWORD_WORDS, None, "ws")
    # TODO
    print("Testing dict-based Crossword generation")
    cw = Crossword(RANDOM_CROSSWORD_WORDS, None, "cw")


if __name__ == "__main__":
    demo_crosswords()
