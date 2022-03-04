import pathlib
import random
import tempfile

import pytest
from PyPDF2 import PdfFileReader

from word_search_generator import WordSearch, config, export, utils


@pytest.fixture()
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield pathlib.Path(temp_dir)


WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"


def generate_test_key(length: int):
    """Generate a test answer key of size `length`."""
    key = {}
    for i in range(length):
        word = utils.get_random_words(1)
        start = (random.randint(0, 9), random.randint(0, 9))
        direction = random.choice(list(config.dir_moves))
        key[word] = {"start": start, "direction": direction}
    return key


def test_export_pdf_puzzles(temp_dir):
    """Export a bunch of puzzles as PDF and make sure they are all 1-page."""
    sizes = [s for s in range(config.min_puzzle_size, config.max_puzzle_size)]
    keys = [k for k in range(3, config.max_puzzle_words, 9)]
    puzzles = []
    pages = set()
    for s in sizes:
        for k in keys:
            puzzle = [["X"] * s for _ in range(s)]
            key = generate_test_key(k)
            level = random.randint(1, 3)
            path = pathlib.Path.joinpath(
                temp_dir, f"test_s{s}_l{level}_k{len(key)}.pdf"
            )
            puzzles.append(path)
            export.write_pdf_file(path, puzzle, key, level)
    for p in puzzles:
        pdf = PdfFileReader(open(p, "rb"))
        pages.add(pdf.getNumPages())
    assert pages == {1}


def test_export_overwrite_file_error(temp_dir):
    """Try to export a puzzle with the name of a file that is already present."""
    path = pathlib.Path.joinpath(temp_dir, "test.pdf")
    path.touch()
    with pytest.raises(FileExistsError):
        export.validate_path(path)


def test_export_pdf_no_extension_provided(temp_dir):
    """Try to export a puzzle with no extension on the path."""
    puzzle = WordSearch(WORDS)
    path = pathlib.Path.joinpath(temp_dir, "test")
    puzzle.save(path)
    correct_path = path.with_suffix(".pdf")
    assert correct_path.exists()


def test_export_pdf_os_error(temp_dir):
    """Try to export a puzzle to a place you don't have access to."""
    puzzle = WordSearch(WORDS)
    with pytest.raises(OSError):
        puzzle.save("/test.pdf")


def test_export_csv_os_error():
    """Try to export a puzzle to a place you don't have access to."""
    puzzle = WordSearch(WORDS)
    with pytest.raises(OSError):
        puzzle.save("/test.csv")
