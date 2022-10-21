import json
import pathlib

import pytest

from word_search_generator import WordSearch, config, utils
from word_search_generator.config import level_dirs
from word_search_generator.types import Direction, Key, Puzzle, Word
from word_search_generator.utils import get_random_words

WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"


def check_key(key: Key, puzzle: Puzzle) -> bool:
    """Test the puzzle key against the current puzzle state."""
    for word, info in key.items():
        row, col = info["start"]  # type: ignore
        d = info["direction"]  # type: ignore
        for char in word:
            if puzzle[row][col] != char:  # type: ignore
                return False
            row += d.r_move  # type: ignore
            col += d.c_move  # type: ignore
    return True


def test_empty_object():
    puzzle = WordSearch()
    assert len(puzzle.words) == 0


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
    assert puzzle.directions == utils.validate_level(config.level_dirs[3])


def test_set_secret_level():
    puzzle = WordSearch(WORDS)
    puzzle.secret_directions = 4  # type: ignore
    assert puzzle.secret_directions == utils.validate_level(4)  # type: ignore


def test_bad_puzzle_level_value():
    puzzle = WordSearch(WORDS)
    with pytest.raises(ValueError):
        puzzle.level = 757


def test_bad_puzzle_level_type():
    puzzle = WordSearch(WORDS)
    with pytest.raises(TypeError):
        puzzle.level = "A"  # type: ignore


def test_garbage_puzzle_level_type():
    puzzle = WordSearch(WORDS)
    with pytest.raises(TypeError):
        puzzle.level = 17.76  # type: ignore


def test_manual_level_control():
    puzzle = WordSearch(WORDS)
    tst_dirs = [Direction.E, Direction.SW, (-1, 0)]
    puzzle.directions = tst_dirs  # type: ignore
    assert puzzle.directions == utils.validate_level(tst_dirs)


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
    assert Word("test") in puzzle.words


def test_add_regular_words_replacing_secret_word():
    puzzle = WordSearch(WORDS)
    puzzle.add_words("test", True)
    puzzle.add_words("test")
    assert Word("test") not in puzzle.secret_words and Word("test") in puzzle.words


def test_add_secret_words():
    puzzle = WordSearch(WORDS)
    puzzle.add_words("test", True)
    assert Word("test") in puzzle.secret_words


def test_add_secret_words_replacing_regular_word():
    puzzle = WordSearch(WORDS)
    puzzle.add_words("test")
    puzzle.add_words("test", True)
    assert (
        Word("test") not in puzzle.hidden_words and Word("test") in puzzle.secret_words
    )


def test_remove_words():
    puzzle = WordSearch(WORDS)
    puzzle.remove_words("test")
    assert "test".upper() not in puzzle.words


def test_remove_words_from_secret_words():
    puzzle = WordSearch(WORDS)
    puzzle.add_words("test", True)
    puzzle.remove_words("test")
    assert "test".upper() not in puzzle.words.union(puzzle.secret_words)


def test_replace_words():
    puzzle = WordSearch(WORDS)
    puzzle.replace_words("set, of replaced, words")
    assert len(puzzle.words) == 4


def test_replace_secret_words():
    puzzle = WordSearch(WORDS, secret_words="secret, blind, nope")
    puzzle.replace_words("hidden", True)
    assert len(puzzle.secret_words) == 1


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
    key_chars.add("")
    assert puzzle_chars == key_chars


def test_puzzle_repr():
    puzzle = WordSearch(WORDS)
    assert eval(repr(puzzle)) == puzzle


def test_puzzle_equal():
    puzzle1 = WordSearch(WORDS, size=10)
    puzzle2 = WordSearch(WORDS, size=10)
    assert puzzle1 == puzzle2


def test_puzzle_invalid_equality():
    puzzle1 = WordSearch(WORDS, size=10)
    puzzle2 = ["testing"]
    assert puzzle1 != puzzle2


def test_puzzle_non_equal():
    puzzle1 = WordSearch(WORDS, size=10)
    puzzle2 = WordSearch(WORDS, size=15)
    assert puzzle1 != puzzle2


def test_puzzle_str():
    puzzle = WordSearch(WORDS)
    puzzle_str = utils.format_puzzle_for_show(puzzle)
    assert str(puzzle) == puzzle_str


def test_puzzle_str_output(capsys):
    puzzle = WordSearch(WORDS)
    print(utils.format_puzzle_for_show(puzzle))
    capture1 = capsys.readouterr()
    print(puzzle)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output(capsys):
    puzzle = WordSearch(WORDS)
    print(utils.format_puzzle_for_show(puzzle))
    capture1 = capsys.readouterr()
    puzzle.show()
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output_for_empty_object(capsys):
    p = WordSearch()
    p.show()
    capture = capsys.readouterr()

    assert capture.out == "Empty puzzle.\n"


def test_puzzle_show_str_output_for_empty_object(capsys):
    p = WordSearch()
    print(p)
    capture = capsys.readouterr()

    assert capture.out == "Empty puzzle.\n"


def test_puzzle_show_solution_output(capsys):
    puzzle = WordSearch(WORDS)
    print(utils.format_puzzle_for_show(puzzle, True))
    capture1 = capsys.readouterr()
    puzzle.show(True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_json_output_property_for_puzzle():
    words = get_random_words(10)
    p = WordSearch(words, level=3)
    assert json.loads(p.json)["puzzle"] == p.puzzle


def test_json_output_property_for_key():
    words = get_random_words(10)
    p = WordSearch(words, level=3)
    json_key = json.loads(p.json)["key"]
    for word, info in json_key.items():
        pos = (info["start_row"], info["start_col"])
        assert pos == p.key[word]["start"]


def test_json_output_property_for_empty_object():
    p = WordSearch()
    assert p.json == json.dumps({})


def test_input_including_palindrome():
    puzzle = WordSearch(WORDS + ", level")
    assert len(puzzle.words) == 8


def test_for_empty_spaces():
    for _ in range(100):
        words = get_random_words(10)
        p = WordSearch(words, level=3)
        flat = [item for sublist in p.puzzle for item in sublist]
        assert p.size * p.size == len(flat)


def test_puzzle_with_secret_words():
    puzzle = WordSearch(WORDS, secret_words=WORDS + ", dewlap")
    assert len(puzzle.secret_words) == 1  # should all be ignored due to overlap


def test_clearing_secret_directions():
    puzzle = WordSearch(WORDS, secret_level=1)
    puzzle.secret_directions = set()
    assert puzzle.secret_directions is None


def test_get_level():
    puzzle = WordSearch(WORDS)
    puzzle.level = 2
    assert puzzle.level == level_dirs[2]  # type: ignore


def test_add_words_with_resize():
    puzzle = WordSearch(WORDS)
    puzzle.size = 5
    puzzle.add_words("test", reset_size=True)
    assert puzzle.size != 5


def test_add_secret_words_with_resize():
    puzzle = WordSearch(WORDS)
    puzzle.size = 5
    puzzle.add_words("test", True, reset_size=True)
    assert puzzle.size != 5


def test_remove_words_with_resize():
    puzzle = WordSearch(WORDS)
    puzzle.size = 5
    puzzle.remove_words("test", reset_size=True)
    assert puzzle.size != 5


def test_replace_words_with_resize():
    puzzle = WordSearch(WORDS)
    puzzle.size = 5
    puzzle.replace_words("set, of replaced, words", reset_size=True)
    assert puzzle.size != 5


def test_no_placed_words():
    p = WordSearch()
    assert len(p.placed_words) == 0


def test_no_hidden_words():
    p = WordSearch()
    assert len(p.placed_words) == 0


def test_placed_hidden_words():
    p = WordSearch("cat bat rat")
    assert len(p.placed_hidden_words) == len(
        {word for word in p.hidden_words if word.position}
    )


def test_placed_secret_words():
    p = WordSearch("pig horse cow", secret_words="cat bat rat")
    assert len(p.placed_secret_words) == len(
        {word for word in p.secret_words if word.position}
    )
