import json
import pathlib

import pytest

from word_search_generator import Key, Puzzle, WordSearch, config, utils
from word_search_generator.config import level_dirs
from word_search_generator.utils import get_random_words
from word_search_generator.word import Direction, Word

WORDS = "dog, cat, pig, horse, donkey, turtle, goat, sheep"

# TODO: test for p = WordSearch(size=15)


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
    ws = WordSearch()
    assert len(ws.words) == 0


def test_input_cleanup():
    ws = WordSearch(WORDS)
    assert len(ws.words) == 8


def test_junky_input_cleanup():
    junky_words = """here, are,                  a, don't

    it's what's,
    junk,,,,,,   , ,i

    words,"""
    junk_ws = WordSearch(junky_words)
    assert len(junk_ws.words) == 4


def test_set_puzzle_level():
    ws = WordSearch(WORDS)
    ws.level = 3
    assert ws.directions == utils.validate_level(config.level_dirs[3])


def test_set_secret_level():
    ws = WordSearch(WORDS)
    ws.secret_directions = 4  # type: ignore
    assert ws.secret_directions == utils.validate_level(4)  # type: ignore


def test_bad_puzzle_level_value():
    ws = WordSearch(WORDS)
    with pytest.raises(ValueError):
        ws.level = 757


def test_bad_puzzle_level_type():
    ws = WordSearch(WORDS)
    with pytest.raises(TypeError):
        ws.level = "A"  # type: ignore


def test_garbage_puzzle_level_type():
    ws = WordSearch(WORDS)
    with pytest.raises(TypeError):
        ws.level = 17.76  # type: ignore


def test_manual_level_control():
    ws = WordSearch(WORDS)
    tst_dirs = [Direction.E, Direction.SW, (-1, 0)]
    ws.directions = tst_dirs  # type: ignore
    assert ws.directions == utils.validate_level(tst_dirs)


def test_set_puzzle_size():
    ws = WordSearch(WORDS)
    ws.size = 15
    assert len(ws.puzzle) == 15


def test_bad_puzzle_size_value():
    ws = WordSearch(WORDS)
    with pytest.raises(ValueError):
        ws.size = 1


def test_bad_puzzle_size_type():
    ws = WordSearch(WORDS)
    with pytest.raises(TypeError):
        ws.size = "A"  # type: ignore


def test_puzzle_key():
    ws = WordSearch(WORDS)
    assert check_key(ws.key, ws.puzzle)


def test_export_pdf(tmp_path):
    ws = WordSearch(WORDS)
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.pdf")
    ws.save(tmp_path)
    assert tmp_path.exists()


def test_export_csv(tmp_path):
    ws = WordSearch(WORDS)
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.csv")
    ws.save(tmp_path)
    assert tmp_path.exists()


def test_invalid_save_path():
    ws = WordSearch(WORDS)
    with pytest.raises(OSError):
        ws.save("~/some/random/dir/that/doesnt/exists")


def test_add_words():
    ws = WordSearch(WORDS)
    ws.add_words("test")
    assert Word("test") in ws.words


def test_add_regular_words_replacing_secret_word():
    ws = WordSearch(WORDS)
    ws.add_words("test", True)
    ws.add_words("test")
    assert Word("test") not in ws.secret_words and Word("test") in ws.words


def test_add_secret_words():
    ws = WordSearch(WORDS)
    ws.add_words("test", True)
    assert Word("test") in ws.secret_words


def test_add_secret_words_replacing_regular_word():
    ws = WordSearch(WORDS)
    ws.add_words("test")
    ws.add_words("test", True)
    assert Word("test") not in ws.hidden_words and Word("test") in ws.secret_words


def test_remove_words():
    ws = WordSearch(WORDS)
    ws.add_words("test")
    ws.remove_words("test")
    assert Word("test") not in ws.words


def test_remove_words_from_secret_words():
    ws = WordSearch(WORDS)
    ws.add_words("test", True)
    ws.remove_words("test")
    assert "test".upper() not in ws.words.union(ws.secret_words)


def test_replace_words():
    ws = WordSearch(WORDS)
    ws.replace_words("set, of replaced, words")
    assert len(ws.words) == 4


def test_replace_secret_words():
    ws = WordSearch(WORDS, secret_words="secret, blind, nope")
    ws.replace_words("hidden", True)
    assert len(ws.secret_words) == 1


def test_reset_puzzle_size():
    ws = WordSearch(WORDS)
    prev_size = ws.size
    ws.size = 25
    ws.reset_size()
    assert ws.size == prev_size


def test_puzzle_repr():
    ws = WordSearch(WORDS)
    assert eval(repr(ws)) == ws


def test_puzzle_equal():
    ws1 = WordSearch(WORDS, size=10)
    ws2 = WordSearch(WORDS, size=10)
    assert ws1 == ws2


def test_puzzle_invalid_equality():
    ws1 = WordSearch(WORDS, size=10)
    ws2 = ["testing"]
    assert ws1 != ws2


def test_puzzle_non_equal():
    ws1 = WordSearch(WORDS, size=10)
    ws2 = WordSearch(WORDS, size=15)
    assert ws1 != ws2


def test_puzzle_str():
    ws = WordSearch(WORDS)
    puzzle_str = utils.format_puzzle_for_show(ws)
    assert str(ws) == puzzle_str


def test_puzzle_str_output(capsys):
    ws = WordSearch(WORDS)
    print(utils.format_puzzle_for_show(ws))
    capture1 = capsys.readouterr()
    print(ws)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output(capsys):
    ws = WordSearch(WORDS)
    print(utils.format_puzzle_for_show(ws))
    capture1 = capsys.readouterr()
    ws.show()
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
    ws = WordSearch(WORDS)
    print(utils.format_puzzle_for_show(ws, True))
    capture1 = capsys.readouterr()
    ws.show(True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_json_output_property_for_puzzle():
    words = get_random_words(10)
    ws = WordSearch(words, level=3)
    assert json.loads(ws.json)["puzzle"] == ws.puzzle


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
    ws = WordSearch(WORDS + ", level")
    assert len(ws.words) == 8


def test_for_empty_spaces():
    for _ in range(100):
        words = get_random_words(10)
        ws = WordSearch(words, level=3)
        flat = [item for sublist in ws.puzzle for item in sublist]
        assert ws.size * ws.size == len(flat)


def test_puzzle_with_secret_words():
    ws = WordSearch(WORDS, secret_words=WORDS + ", dewlap")
    assert len(ws.secret_words) == 1  # should all be ignored due to overlap


def test_clearing_secret_directions():
    ws = WordSearch(WORDS, secret_level=1)
    ws.secret_directions = set()
    assert ws.secret_directions is None


def test_get_level():
    ws = WordSearch(WORDS)
    ws.level = 2
    assert ws.level == level_dirs[2]  # type: ignore


def test_add_words_with_resize():
    ws = WordSearch(WORDS)
    ws.size = 5
    ws.add_words("test", reset_size=True)
    assert ws.size != 5


def test_add_secret_words_with_resize():
    ws = WordSearch(WORDS)
    ws.size = 5
    ws.add_words("test", True, reset_size=True)
    assert ws.size != 5


def test_remove_words_with_resize():
    ws = WordSearch(WORDS)
    ws.size = 5
    ws.remove_words("test", reset_size=True)
    assert ws.size != 5


def test_replace_words_with_resize():
    ws = WordSearch(WORDS)
    ws.size = 5
    ws.replace_words("set, of replaced, words", reset_size=True)
    assert ws.size != 5


def test_no_placed_words():
    p = WordSearch()
    assert len(p.placed_words) == 0


def test_no_hidden_words():
    p = WordSearch()
    assert len(p.placed_words) == 0


def test_placed_hidden_words():
    p = WordSearch("cat bat rat")
    assert len(p.placed_hidden_words) == len(
        {word for word in p.hidden_words if word.direction}
    )


def test_placed_secret_words():
    p = WordSearch("pig horse cow", secret_words="cat bat rat")
    assert len(p.placed_secret_words) == len(
        {word for word in p.secret_words if word.direction}
    )


def test_random_words_only():
    p = WordSearch(size=25)
    p.random_words(5)
    assert len(p.placed_words) == 5


def test_random_words_added():
    p = WordSearch("mispelled", size=25)
    p.random_words(5)
    assert len(p.placed_words) == 6
