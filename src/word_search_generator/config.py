from enum import Enum, unique

# puzzle settings
min_puzzle_size = 10
max_puzzle_size = 25
min_puzzle_words = 1
max_puzzle_words = 30
max_fit_tries = 100


@unique
class Direction(Enum):
    """
    If you want custom directions, like `"skipE": (0, 2)`, this is the
    place to monkey-patch them in.

    Tuples are listed in (∂row, ∂col) pairs, presumably b/c that makes
    it easier to use with the Puzzle = list[list[chr]] format
    """

    N = (-1, 0)
    NE = (-1, 1)
    E = (0, 1)
    SE = (1, 1)
    S = (1, 0)
    SW = (1, -1)
    W = (0, -1)
    NW = (-1, -1)

    @property
    def r_move(self) -> int:
        return self.value[0]  # type: ignore

    @property
    def c_move(self) -> int:
        return self.value[1]  # type: ignore


level_dirs = {
    1: {"E", "S"},
    2: {"NE", "E", "SE", "S"},
    3: {"N", "NE", "E", "SE", "S", "SW", "W", "NW"},
    4: {"N", "NE", "SE", "SW", "W", "NW"},  # no E or S for better hiding
    8: {"N", "S", "E", "W"},  # no diagonals
    7: {"NE", "SE", "NW", "SW"},  # diagonals only
}

# pdf export settings
pdf_author = "Josh Duncan"
pdf_creator = "word-search @ joshbduncan.com"
pdf_title = "Word Search Puzzle"
pdf_title_font_size = 18
pdf_font_size = 12
pdf_key_font_size = 6
pdf_font_adjust = 21
pdf_puzzle_width = 7
