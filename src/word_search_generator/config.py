from __future__ import annotations

from .word import Direction

# puzzle settings
min_puzzle_size = 5
max_puzzle_size = 50
min_puzzle_words = 1
max_puzzle_words = 100
max_fit_tries = 100

# puzzle grid settings
ACTIVE = "*"
INACTIVE = "#"

# puzzle difficulty levels
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
pdf_font_size_XXL = 18
pdf_font_size_XL = 15
pdf_font_size_L = 12
pdf_font_size_M = 9
pdf_font_size_S = 5
pdf_puzzle_width = 7  # inches
