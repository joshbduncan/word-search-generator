from copy import deepcopy
from enum import Enum
from math import sqrt, ceil

from word_search_generator import WordSearch
from word_search_generator.core import Generator, GameType
from word_search_generator.core.game import Puzzle, MissingWordError


class CellType(Enum):
    OUTSIDE = " "
    INSIDE = "X"
    HEAD = "*"
    LETTER = "+"


def color_cells(p: Puzzle) -> Puzzle:
    p = deepcopy(p)
    # 1. color the letters
    # 2. color the outside
    # 3. remaining cells given the inside treatment


class CrosswordFromWordSearch(Generator):
    def generate(self, game: GameType) -> Puzzle:
        # Try generating increasingly-large WordSearch until all words fit
        size = ceil(sqrt(len("".join(str(w) for w in game.words))) + 1)
        success = False

        while not success:
            try:
                ws = WordSearch(
                    level=1,
                    size=size,
                    preprocessed_words=game.words,
                    require_all_words=True,
                )
                success = True
            except MissingWordError:
                size += 1
                continue

        print(color_cells(ws.puzzle))


class CrosswordGenerator(Generator):
    def generate(self, game: GameType) -> Puzzle:
        # go nuts with a Dict and forcing intersections
        pass
