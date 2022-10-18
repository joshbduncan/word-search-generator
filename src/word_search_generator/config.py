from enum import Enum, unique

# puzzle settings
min_puzzle_size = 5
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

    # is there a better way to specify typing here?
    # without hints here, the linter gets upset with my definitions of r/c_move
    N: tuple[int, int] = (-1, 0)
    NE: tuple[int, int] = (-1, 1)
    E: tuple[int, int] = (0, 1)
    SE: tuple[int, int] = (1, 1)
    S: tuple[int, int] = (1, 0)
    SW: tuple[int, int] = (1, -1)
    W: tuple[int, int] = (0, -1)
    NW: tuple[int, int] = (-1, -1)

    @property
    def r_move(self) -> int:
        return self.value[0]

    @property
    def c_move(self) -> int:
        return self.value[1]


level_dirs = {
    1: {Direction.E, Direction.S},
    2: {Direction.NE, Direction.E, Direction.SE, Direction.S},
    3: {
        Direction.N,
        Direction.NE,
        Direction.E,
        Direction.SE,
        Direction.S,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    4: {  # no E or S for better hiding
        Direction.N,
        Direction.NE,
        Direction.SE,
        Direction.SW,
        Direction.W,
        Direction.NW,
    },
    8: {Direction.N, Direction.E, Direction.W, Direction.S},  # no diagonals
    7: {Direction.NE, Direction.SE, Direction.NW, Direction.SW},  # diagonals only
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
