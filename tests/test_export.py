import os
import pathlib
import random

import pytest
from PyPDF2 import PdfFileReader

from word_search_generator import WordSearch, config, export, utils

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
    for s in sizes:
        for k in keys:
            puzzle = [["X"] * s for _ in range(s)]
            key = generate_test_key(k)
            level = random.randint(1, 3)
            path = pathlib.Path(f"{temp_dir}/test_s{s}_l{level}_k{len(key)}.pdf")
            export.write_pdf_file(path, puzzle, key, level)
            pdf = PdfFileReader(open(path, "rb"))
            assert pathlib.Path(path).exists() and pdf.getNumPages() == 1


def test_export_to_dir(temp_dir):
    """Try to export a puzzle with only a path to the directory."""
    path = pathlib.Path(f"{temp_dir}")
    fpath = export.validate_path(path, "pdf")
    assert fpath.parent == path


def test_export_overwrite_file_error(temp_dir):
    """Try to export a puzzle with the name of a file that is already present."""
    fname = "dont_overwrite_me.pdf"
    ftype = "pdf"
    fpath = pathlib.Path(f"{temp_dir}/{fname}")
    os.system(f"touch {fpath.as_posix()}")
    with pytest.raises(FileExistsError):
        export.validate_path(fpath, ftype)


def test_export_csv_overwrite_file_os_error(temp_dir):
    """Try to export a puzzle with the name of a file that is already present."""
    puzzle = WordSearch(WORDS)
    fname = "dont_overwrite_me.pdf"
    fpath = pathlib.Path(f"{temp_dir}/{fname}")
    os.chmod(temp_dir, 4)
    # os.system(f"touch {fpath.as_posix()}")
    with pytest.raises(OSError):
        export.write_csv_file(fpath, puzzle.puzzle, puzzle.key, puzzle.level)


def test_export_pdf_overwrite_file_os_error(temp_dir):
    """Try to export a puzzle with the name of a file that is already present."""
    puzzle = WordSearch(WORDS)
    fname = "dont_overwrite_me.pdf"
    fpath = pathlib.Path(f"{temp_dir}/{fname}")
    os.chmod(temp_dir, 4)
    # os.system(f"touch {fpath.as_posix()}")
    with pytest.raises(OSError):
        export.write_pdf_file(fpath, puzzle.puzzle, puzzle.key, puzzle.level)
