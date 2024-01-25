import json
import pathlib
import random
from pathlib import Path

import pytest

from word_search_generator import WordSearch, utils
from word_search_generator.core.directions import LEVEL_DIRS
from word_search_generator.core.game import (
    EmptyPuzzleError,
    EmptyWordlistError,
    Key,
    MissingWordError,
    Puzzle,
    PuzzleSizeError,
)
from word_search_generator.core.validator import NoSingleLetterWords
from word_search_generator.mask.polygon import Rectangle
from word_search_generator.word_search._formatter import WordSearchFormatter

formatter = WordSearchFormatter()


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


def test_puzzle_key(ws: WordSearch):
    assert check_key(ws.key, ws.puzzle)


def test_export_pdf(ws: WordSearch, tmp_path: Path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.pdf")
    ws.save(tmp_path)
    assert tmp_path.exists()


def test_export_csv(ws: WordSearch, tmp_path: Path):
    tmp_path = pathlib.Path.joinpath(tmp_path, "test.csv")
    ws.save(tmp_path)
    assert tmp_path.exists()


def test_invalid_save_path(ws: WordSearch):
    with pytest.raises(OSError):
        ws.save("~/some/random/dir/that/doesnt/exists")


def test_puzzle_repr(ws: WordSearch):
    assert eval(repr(ws)) == ws


def test_puzzle_equality(words):
    ws1 = WordSearch(words, size=10)
    ws2 = WordSearch(words, size=10)
    assert ws1 == ws2


def test_puzzle_inequality(words):
    ws1 = WordSearch(words, size=10)
    ws2 = ["testing"]
    assert ws1 != ws2


def test_puzzle_non_equal(words):
    ws1 = WordSearch(words, size=10)
    ws2 = WordSearch(words, size=15)
    assert ws1 != ws2


def test_puzzle_str(ws: WordSearch):
    puzzle_str = formatter.format_puzzle_for_show(ws)
    assert str(ws) == puzzle_str


def test_puzzle_str_output(ws: WordSearch, capsys):
    print(formatter.format_puzzle_for_show(ws))
    capture1 = capsys.readouterr()
    print(ws)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output(ws: WordSearch, capsys):
    print(formatter.format_puzzle_for_show(ws))
    capture1 = capsys.readouterr()
    ws.show()
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output_lowercase(ws: WordSearch, capsys):
    print(formatter.format_puzzle_for_show(ws, lowercase=True))
    capture1 = capsys.readouterr()
    ws.show(lowercase=True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_solution_output(ws: WordSearch, capsys):
    print(formatter.format_puzzle_for_show(ws, True))
    capture1 = capsys.readouterr()
    ws.show(True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_hide_fillers_output(ws: WordSearch, capsys):
    print(formatter.format_puzzle_for_show(ws, hide_fillers=True))
    capture1 = capsys.readouterr()
    ws.show(hide_fillers=True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out
    assert "\x1b" not in capture2.out


def test_json_empty_puzzle_error(ws: WordSearch):
    assert ws
    ws._puzzle = []
    with pytest.raises(EmptyPuzzleError):
        ws.json


def test_json_output_property_for_puzzle():
    words = ",".join(utils.get_random_words(10))
    ws = WordSearch(words, level=3)
    assert json.loads(ws.json)["puzzle"] == ws.puzzle


def test_json_output_property_for_key():
    words = ",".join(utils.get_random_words(10))
    ws = WordSearch(words, level=3)
    json_key = json.loads(ws.json)["key"]
    for word, info in json_key.items():
        pos = (info["start_row"], info["start_col"])
        assert pos == ws.key[word]["start"]


def test_for_empty_spaces(iterations):
    for _ in range(iterations):
        words = ",".join(utils.get_random_words(10))
        ws = WordSearch(words, level=3)
        flat = [item for sublist in ws.puzzle for item in sublist]
        assert ws.size * ws.size == len(flat)


def test_puzzle_with_secret_words(words):
    ws = WordSearch(words, secret_words=words + ", dewlap")
    assert len(ws.secret_words) == 1  # should all be ignored due to overlap


def test_clearing_secret_directions(words):
    ws = WordSearch(words, secret_level=1)
    with pytest.raises(ValueError):
        ws.secret_directions = set()


def test_get_level(ws: WordSearch):
    ws.level = 2
    assert ws.level == LEVEL_DIRS[2]  # type: ignore


def test_add_words_with_resize(ws: WordSearch):
    ws.size = 5
    ws.add_words("test", reset_size=True)
    assert ws.size != 5


def test_add_secret_words_with_resize(ws: WordSearch):
    ws.size = 5
    ws.add_words("test", True, reset_size=True)
    assert ws.size != 5


def test_remove_words_with_resize(ws: WordSearch):
    ws.size = 5
    ws.remove_words("test", reset_size=True)
    assert ws.size != 5


def test_replace_words_with_resize(ws: WordSearch):
    ws.size = 5
    ws.replace_words("set, of replaced, words", reset_size=True)
    assert ws.size != 5


def test_no_placed_words():
    ws = WordSearch()
    assert len(ws.placed_words) == 0


def test_no_hidden_words():
    ws = WordSearch()
    assert len(ws.placed_words) == 0


def test_placed_hidden_words(ws: WordSearch):
    assert len(ws.placed_hidden_words) == len(
        {word for word in ws.hidden_words if word.direction}
    )


def test_placed_secret_words():
    ws = WordSearch("pig horse cow", secret_words="cat bat rat")
    assert len(ws.placed_secret_words) == len(
        {word for word in ws.secret_words if word.direction}
    )


def test_random_words_only():
    ws = WordSearch()
    ws.random_words(5)
    assert len(ws.words) > 0


def test_random_words_added():
    ws = WordSearch("dog cat rat", size=25)
    ws.random_words(2, "ADD")
    assert len(ws.words) > 3


def test_random_words_count_type_error():
    ws = WordSearch()
    with pytest.raises(TypeError):
        ws.random_words("five")  # type: ignore


def test_random_words_count_value_error():
    ws = WordSearch()
    with pytest.raises(ValueError):
        ws.random_words(500)


def test_random_words_action_type_error():
    ws = WordSearch()
    with pytest.raises(TypeError):
        ws.random_words(5, action=5)  # type: ignore


def test_random_words_action_value_error():
    ws = WordSearch()
    with pytest.raises(ValueError):
        ws.random_words(5, "SUBTRACT")


def test_invalid_size_at_init_value():
    with pytest.raises(ValueError):
        ws = WordSearch(size=250)  # noqa: F841


def test_invalid_size_at_init_type():
    with pytest.raises(TypeError):
        ws = WordSearch(size="250")  # type: ignore  # noqa: F841


def test_puzzle_solution_output(ws: WordSearch, capsys):
    print(formatter.format_puzzle_for_show(ws, True))
    capture1 = capsys.readouterr()
    ws.solution
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_unplaced_words():
    ws = WordSearch("dog", size=5)
    ws.add_words("generator")
    ws.add_words("refrigerator", secret=True)
    assert len(ws.unplaced_words) == 2


def test_unplaced_hidden_words():
    ws = WordSearch("dog", size=5)
    ws.add_words("generator")
    assert len(ws.unplaced_hidden_words) == 1


def test_unplaced_secret_words():
    ws = WordSearch("dog", size=5)
    ws.add_words("generator", secret=True)
    assert len(ws.unplaced_secret_words) == 1


def test_invalid_export_format(ws: WordSearch):
    with pytest.raises(ValueError):
        ws.save("test.pdf", format="GIF")


def test_missing_word_error():
    ws = WordSearch("dog", size=5, require_all_words=True)
    with pytest.raises(MissingWordError):
        ws.add_words("generator")


def test_cropped_puzzle_height(words):
    size = 21
    ws = WordSearch(words, size=size)
    assert len(ws.cropped_puzzle) == size


def test_cropped_puzzle_width(words):
    size = 21
    ws = WordSearch(words, size=size)
    assert len(ws.cropped_puzzle[0]) == size


def test_cropped_puzzle_masked_1(words):
    size = 20
    ws = WordSearch(words, size=size)
    ws.apply_mask(Rectangle(size - 2, size - 2, (1, 1)))
    assert ws.puzzle[1][1] == ws.cropped_puzzle[0][0]
    assert ws.puzzle[size - 2][size - 2] == ws.cropped_puzzle[size - 3][size - 3]


def test_cropped_puzzle_size(words):
    size = 20
    ws = WordSearch(words, size=size)
    rec_w = size - 5
    rec_h = size - 7
    ws.apply_mask(Rectangle(rec_w, rec_h, (1, 1)))
    w, h = ws.cropped_size
    assert w != ws.size
    assert h != ws.size
    assert ws.cropped_size == (rec_w, rec_h)


def test_cropped_puzzle_masked_2(words):
    size = 20
    ws = WordSearch(words, size=size)
    ws.apply_mask(Rectangle(size - 10, size - 10, (1, 1)))
    assert ws.puzzle[1][1] == ws.cropped_puzzle[0][0]
    assert ws.puzzle[size - 10][size - 10] == ws.cropped_puzzle[size - 11][size - 11]


def test_word_placement(iterations, builtin_mask_shapes):
    def check_chars(puzzle, word):
        row, col = word.position
        for c in word.text:
            if c != puzzle[row][col]:
                return False
            row += word.direction.r_move
            col += word.direction.c_move
        return True

    results = []
    for _ in range(iterations):
        ws = WordSearch(size=random.randint(21, 35))
        ws.random_words(random.randint(5, 21))
        mask = random.choice(builtin_mask_shapes)
        if mask:
            ws.apply_mask(mask)
        results.append(all(check_chars(ws.puzzle, word) for word in ws.placed_words))
    assert all(results)


def test_puzzle_size_error():
    ws = WordSearch("abracadabra")
    with pytest.raises(PuzzleSizeError):
        ws.size = 5


def test_hide_fillers(iterations, builtin_mask_shapes):
    results = []
    for _ in range(iterations):
        ws = WordSearch(size=random.randint(21, 35))
        ws.random_words(random.randint(5, 21))
        mask = random.choice(builtin_mask_shapes)
        if mask:
            ws.apply_mask(mask)
        hidden_fillers = formatter.hide_filler_characters(ws)
        chars: set[str] = set()
        for word in ws.placed_words:
            chars.update(hidden_fillers[y][x] for y, x in word.coordinates)
        results.append(" " not in chars)
    assert all(results)


def test_solution_plus_hide_fillers(iterations, builtin_mask_shapes):
    results = []
    for _ in range(iterations):
        ws = WordSearch(size=random.randint(21, 35))
        ws.random_words(random.randint(5, 21))
        mask = random.choice(builtin_mask_shapes)
        if mask:
            ws.apply_mask(mask)
        chars = {c for chars in ws.puzzle for c in chars}
        results.append("\x1b" not in chars)
    assert all(results)


def test_word_directions(words, secret_words):
    """
    Hidden words can go NE, E, SE, or S.
    Secret words go on diagonals.
    Do they all obey the restriction rules?
    """
    ws = WordSearch(words, secret_words=secret_words, secret_level=7)
    assert all(w.direction in ws.directions for w in ws.placed_hidden_words)
    assert all(w.direction in ws.secret_directions for w in ws.placed_secret_words)


def test_validator_setter(words):
    ws = WordSearch(words, validators=None)
    ws.validators = [NoSingleLetterWords()]
    assert all(isinstance(v, NoSingleLetterWords) for v in ws.validators)


def test_validator_setter_invalid_validator(words):
    class Val:
        pass

    with pytest.raises(TypeError):
        WordSearch(words, validators=[Val()])  # type: ignore[list-item]


def test_no_words_to_generate(ws: WordSearch):
    ws._words = set()
    with pytest.raises(EmptyWordlistError):
        ws.generate()
