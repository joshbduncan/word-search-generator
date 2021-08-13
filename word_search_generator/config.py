pdf_author = "Josh Duncan"
pdf_creator = "word-search @ joshbduncan.com"
pdf_title = "Word Search Puzzle"

max_puzzle_size = 25
max_puzzle_words = 30

dir_moves = {
    "N": (-1, 0),
    "NE": (-1, 1),
    "E": (0, 1),
    "SE": (1, 1),
    "S": (1, 0),
    "SW": (1, -1),
    "W": (0, -1),
    "NW": (-1, -1),
}

level_dirs = {
    1: ("E", "S"),
    2: ("NE", "E", "SE", "S"),
    3: ("N", "NE", "E", "SE", "S", "SW", "W", "NW"),
}
