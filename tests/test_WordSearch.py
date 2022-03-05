import pathlib

import pytest

from word_search_generator import WordSearch, config, utils
from word_search_generator.types import Key, Puzzle

WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"


def check_key(key: Key, puzzle: Puzzle) -> bool:
    """Test the puzzle key against the current puzzle state."""
    for word, info in key.items():
        row, col = info["start"]
        rmove, cmove = config.dir_moves[info["direction"]]
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


def test_generate_with_level_option():
    puzzle = WordSearch(WORDS)
    puzzle.generate(level=2)
    assert puzzle.level == 2


def test_generate_with_size_option():
    puzzle = WordSearch(WORDS)
    puzzle.generate(size=22)
    assert puzzle.size == 22


def test_set_puzzle_level():
    puzzle = WordSearch(WORDS)
    puzzle.level = 3
    assert puzzle.level == 3


def test_bad_puzzle_level_value():
    puzzle = WordSearch(WORDS)
    with pytest.raises(ValueError):
        puzzle.level = 7


def test_bad_puzzle_level_type():
    puzzle = WordSearch(WORDS)
    with pytest.raises(TypeError):
        puzzle.level = "A"


def test_set_puzzle_size():
    puzzle = WordSearch(WORDS)
    puzzle.size = 15
    assert len(puzzle.puzzle) == 15


def test_bad_puzzle_size_value():
    puzzle = WordSearch(WORDS)
    with pytest.raises(ValueError):
        puzzle.size = 1


def test_bad_puzzle_size_type():
    puzzle = WordSearch(WORDS)
    with pytest.raises(TypeError):
        puzzle.size = "A"


def test_puzzle_key():
    puzzle = WordSearch(WORDS)
    assert check_key(puzzle.key, puzzle.puzzle)


def test_export_pdf(tmp_path):
    puzzle = WordSearch(WORDS)
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.pdf")
    puzzle.save(tmp_path)
    assert tmp_path.exists()


def test_export_csv(tmp_path):
    puzzle = WordSearch(WORDS)
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.csv")
    puzzle.save(tmp_path)
    assert tmp_path.exists()


def test_invalid_save_path():
    puzzle = WordSearch(WORDS)
    with pytest.raises(OSError):
        puzzle.save("~/some/random/dir/that/doesnt/exists")


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
    prev_size = puzzle.size
    puzzle.size = 25
    puzzle.reset_size()
    assert puzzle.size == prev_size


def test_puzzle_solution():
    # need to check for overlaps
    puzzle = WordSearch(WORDS)
    print(puzzle.solution)
    puzzle_chars = set([char for line in puzzle.solution for char in line])
    key_chars = set([char for word in puzzle.key for char in word])
    key_chars.add("•")
    assert puzzle_chars == key_chars


def test_puzzle_repr():
    puzzle = WordSearch(WORDS)
    assert repr(puzzle) == f"WordSearch('{puzzle.words}')"


def test_puzzle_str():
    puzzle = WordSearch(WORDS)
    puzzle_str = f"""
** WORD SEARCH PUZZLE **

{utils.stringify(puzzle.puzzle)}

Find these words: {utils.get_word_list_str(puzzle.key)}

* Words can go {utils.get_level_dirs_str(puzzle.level)}.

Answer Key: {utils.get_answer_key_str(puzzle.key)}"""
    assert str(puzzle) == str(puzzle_str)


def test_puzzle_str_output(capsys):
    puzzle = WordSearch(WORDS)
    puzzle_str = f"""
** WORD SEARCH PUZZLE **

{utils.stringify(puzzle.puzzle)}

Find these words: {utils.get_word_list_str(puzzle.key)}

* Words can go {utils.get_level_dirs_str(puzzle.level)}.

Answer Key: {utils.get_answer_key_str(puzzle.key)}
"""
    print(puzzle)
    captured = capsys.readouterr()
    assert captured.out == puzzle_str


def test_puzzle_show_solution_output(capsys):
    puzzle = WordSearch(WORDS)
    solution_str = f"""
** WORD SEARCH SOLUTION **

{utils.stringify(puzzle.solution)}
"""
    puzzle.show_solution()
    captured = capsys.readouterr()
    assert captured.out == solution_str
