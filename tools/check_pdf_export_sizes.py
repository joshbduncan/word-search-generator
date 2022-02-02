import pathlib
import random
import string

from word_search_generator import config
from word_search_generator.export import write_pdf_file

TEMP_DIR = "/Users/jbd/Desktop/sample-puzzles"


def random_word_generator(length: int = 6, chars: str = string.ascii_uppercase) -> str:
    """Generate a random fake word size `length`."""
    return "".join(random.choice(chars) for _ in range(length))


def generate_test_key(length: int) -> dict:
    """Generate a test answer key of size `length`."""
    key = {}
    for i in range(length):
        word = random_word_generator(random.randint(3, 10))
        start = (random.randint(0, 9), random.randint(0, 9))
        direction = random.choice(list(config.dir_moves))
        key[word] = {"start": start, "direction": direction}
    return key


def test_export_pdf_puzzles():
    """Export a bunch of puzzles as PDF and make sure they are all 1-page."""
    sizes = [s for s in range(config.min_puzzle_size, config.max_puzzle_size + 1)]
    keys = [k for k in range(3, config.max_puzzle_words + 1, 9)]
    for s in sizes:
        for k in keys:
            puzzle = [["X"] * s for _ in range(s)]
            key = generate_test_key(k)
            level = random.randint(1, 3)
            path = pathlib.Path(f"{TEMP_DIR}/test_s{s}_l{level}_k{len(key)}.pdf")
            write_pdf_file(path, puzzle, key, level)


if __name__ == "__main__":
    test_export_pdf_puzzles()
