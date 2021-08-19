import pathlib
import pytest
import tempfile

from word_search_generator import WordSearch
from word_search_generator.config import dir_moves


WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"
TEMP_DIR = tempfile.TemporaryDirectory()


def check_key(key: dict, puzzle: list) -> bool:
    """Test the puzzle key against the current puzzle state."""
    for word, info in key.items():
        row, col = info["start"]
        rmove, cmove = dir_moves[info["direction"]]
        for char in word:
            if puzzle[row][col] != char:
                return False
            row += rmove
            col += cmove
    return True


def test_input_cleanup():
    puzzle = WordSearch(WORDS)
    assert len(puzzle.words) == 8


def test_junky_input_cleanup():
    junky_words = """here, are,                  a, don't

    it's what's,
    junk,,,,,,   , ,i

    words,"""
    junk_puzzle = WordSearch(junky_words)
    assert len(junk_puzzle.words) == 4


def test_set_puzzle_level():
    puzzle = WordSearch(WORDS)
    puzzle.level = 3
    assert puzzle.level == 3


def test_bad_puzzle_level_value():
    puzzle = WordSearch(WORDS)
    with pytest.raises(ValueError):
        puzzle.level = 7


def test_set_puzzle_size():
    puzzle = WordSearch(WORDS)
    puzzle.size = 15
    assert len(puzzle.puzzle) == 15


def test_bad_puzzle_size_value():
    puzzle = WordSearch(WORDS)
    with pytest.raises(ValueError):
        puzzle.size = 1


def test_puzzle_key():
    puzzle = WordSearch(WORDS)
    assert check_key(puzzle.key, puzzle.puzzle)


def test_export_pdf():
    puzzle = WordSearch(WORDS)
    temp_path = TEMP_DIR.name + "test.pdf"
    puzzle.save(temp_path, "pdf")
    assert pathlib.Path(temp_path).exists()


def test_export_csv():
    puzzle = WordSearch(WORDS)
    temp_path = TEMP_DIR.name + "test.csv"
    puzzle.save(temp_path, "csv")
    assert pathlib.Path(temp_path).exists()


def test_invalid_save_path():
    puzzle = WordSearch(WORDS)
    with pytest.raises(FileNotFoundError):
        temp_dir = tempfile.TemporaryDirectory()
        temp_dir.cleanup()
        puzzle.save(temp_dir.name, "csv")


def test_add_words():
    puzzle = WordSearch(WORDS)
    puzzle.add_words("test")
    assert "test".upper() in puzzle.words


def test_remove_words():
    puzzle = WordSearch(WORDS)
    puzzle.remove_words("test")
    assert "test".upper() not in puzzle.words


def test_replace_words():
    puzzle = WordSearch(WORDS)
    puzzle.replace_words("set, of replaced, words")
    assert len(puzzle.words) == 4


def test_reset_puzzle_size():
    puzzle = WordSearch(WORDS)
    prev_size = len(puzzle.puzzle)
    puzzle.size = 20
    puzzle.reset_size()
    assert len(puzzle.puzzle) == prev_size


TEMP_DIR.cleanup()
