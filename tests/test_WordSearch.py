import pathlib

import pytest

from word_search_generator import WordSearch, config, utils
from word_search_generator.types import Key, Puzzle
from word_search_generator.utils import get_random_words

WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"


def check_key(key: Key, puzzle: Puzzle) -> bool:
    """Test the puzzle key against the current puzzle state."""
    for word, info in key.items():
        row, col = info["start"]
        rmove, cmove = config.dir_moves[info["direction"]]
        for char in word:
            if puzzle[row - 1][col - 1] != char:
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
        puzzle.level = "A"  # type: ignore


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
        puzzle.size = "A"  # type: ignore


def test_puzzle_key():
    puzzle = WordSearch(WORDS)
    for r in puzzle.puzzle:
        print(" ".join(r))
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
    puzzle_str = f"""{utils.make_header(puzzle.puzzle, "WORD SEARCH")}
{utils.stringify(puzzle.puzzle)}

Find these words: {utils.get_word_list_str(puzzle.key)}

* Words can go {utils.get_level_dirs_str(puzzle.level)}.

Answer Key: {utils.get_answer_key_str(puzzle.key)}"""
    assert str(puzzle) == str(puzzle_str)


def test_puzzle_str_output(capsys):
    puzzle = WordSearch(WORDS)
    puzzle_str = f"""{utils.make_header(puzzle.puzzle, "WORD SEARCH")}
{utils.stringify(puzzle.puzzle)}

Find these words: {utils.get_word_list_str(puzzle.key)}

* Words can go {utils.get_level_dirs_str(puzzle.level)}.

Answer Key: {utils.get_answer_key_str(puzzle.key)}
"""
    print(puzzle)
    captured = capsys.readouterr()
    assert captured.out == puzzle_str


def test_puzzle_show_output(capsys):
    puzzle = WordSearch(WORDS)
    puzzle_str = f"""{utils.make_header(puzzle.puzzle, "WORD SEARCH")}
{utils.stringify(puzzle.puzzle)}

Find these words: {utils.get_word_list_str(puzzle.key)}

* Words can go {utils.get_level_dirs_str(puzzle.level)}.

Answer Key: {utils.get_answer_key_str(puzzle.key)}
"""
    puzzle.show()
    captured = capsys.readouterr()
    assert captured.out == puzzle_str


def test_puzzle_show_solution_output(capsys):
    puzzle = WordSearch(WORDS)
    output_puzzle = utils.highlight_solution(puzzle.puzzle, solution=puzzle.solution)
    solution_str = f"""{utils.make_header(puzzle.puzzle, "PUZZLE SOLUTION")}
{utils.stringify(output_puzzle)}

Find these words: {utils.get_word_list_str(puzzle.key)}

* Words can go {utils.get_level_dirs_str(puzzle.level)}.

Answer Key: {utils.get_answer_key_str(puzzle.key)}
"""
    puzzle.show(solution=True)
    captured = capsys.readouterr()
    assert captured.out == solution_str


def test_input_including_palindrome():
    puzzle = WordSearch(WORDS + ", level")
    assert len(puzzle.words) == 8


def test_for_empty_spaces():
    for _ in range(100):
        words = get_random_words(10)
        p = WordSearch(words, level=3)
        flat = [item for sublist in p.puzzle for item in sublist]
        assert "•" not in flat
