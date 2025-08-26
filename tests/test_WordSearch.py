import json
import pathlib
import random
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from rich.color import ColorSystem
from rich.console import Console

from word_search_generator import WordSearch
from word_search_generator.core.directions import LEVEL_DIRS
from word_search_generator.core.game import (
    EmptyPuzzleError,
    EmptyWordlistError,
    Key,
    MissingWordError,
    Puzzle,
    PuzzleSizeError,
    WordSet,
)
from word_search_generator.core.validator import NoSingleLetterWords
from word_search_generator.mask.polygon import Rectangle
from word_search_generator.utils import get_random_words
from word_search_generator.word_search._formatter import WordSearchFormatter

if TYPE_CHECKING:
    from word_search_generator.mask import Mask


formatter: WordSearchFormatter = WordSearchFormatter()


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
        ws.save("~/some/random/dir/that/does/not/exists")


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
    puzzle_str = formatter.show(ws)
    assert str(ws) == puzzle_str


def test_puzzle_str_output(ws: WordSearch, capsys):
    print(formatter.show(ws))
    capture1 = capsys.readouterr()
    print(ws)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output(ws: WordSearch, capsys):
    print(formatter.show(ws))
    capture1 = capsys.readouterr()
    ws.show()
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_output_lowercase(ws: WordSearch, capsys):
    print(formatter.show(ws, lowercase=True))
    capture1 = capsys.readouterr()
    ws.show(lowercase=True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out


def test_puzzle_show_solution_output(ws: WordSearch, capsys):
    print(formatter.show(ws, solution=True))

    captured_1 = capsys.readouterr()
    stdout_1 = captured_1.out
    stderr_1 = captured_1.err

    assert stdout_1
    assert not stderr_1

    ws.show(True)

    captured_2 = capsys.readouterr()
    stdout_2 = captured_2.out
    stderr_2 = captured_2.err

    assert stdout_2
    assert not stderr_2

    assert stdout_1 == stdout_2


def test_puzzle_show_hide_fillers_output(ws: WordSearch, capsys):
    print(formatter.show(ws, hide_fillers=True))
    capture1 = capsys.readouterr()
    ws.show(hide_fillers=True)
    capture2 = capsys.readouterr()
    assert capture1.out == capture2.out
    assert "\x1b" not in capture2.out


def test_json_empty_puzzle_error(ws: WordSearch):
    assert ws
    ws._puzzle = []
    with pytest.raises(EmptyPuzzleError):
        ws.json  # noqa: B018


def test_json_output_property_for_puzzle():
    words = ",".join(get_random_words(10))
    ws: WordSearch = WordSearch(words, level=3)
    assert json.loads(ws.json)["puzzle"] == ws.puzzle


def test_json_output_property_for_key():
    words = ",".join(get_random_words(10))
    ws: WordSearch = WordSearch(words, level=3)
    json_key = json.loads(ws.json)["key"]
    for word, info in json_key.items():
        pos = (info["start_row"], info["start_col"])
        assert pos == ws.key[word]["start"]


@pytest.mark.repeat(10)
def test_for_empty_spaces():
    words = ",".join(get_random_words(10))
    ws: WordSearch = WordSearch(words, level=3)
    flat = [item for sublist in ws.puzzle for item in sublist]
    assert ws.size * ws.size == len(flat)


def test_puzzle_with_secret_words(words):
    ws: WordSearch = WordSearch(words, secret_words=words + ", dewlap")
    assert len(ws.secret_words) == 1  # should all be ignored due to overlap


def test_clearing_secret_directions(words):
    ws: WordSearch = WordSearch(words, secret_level=1)
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
    ws: WordSearch = WordSearch()
    assert len(ws.placed_words) == 0


def test_no_hidden_words():
    ws: WordSearch = WordSearch()
    assert len(ws.placed_words) == 0


def test_placed_hidden_words(ws: WordSearch):
    assert len(ws.placed_hidden_words) == len(
        {word for word in ws.hidden_words if word.direction}
    )


def test_placed_secret_words():
    ws: WordSearch = WordSearch("pig horse cow", secret_words="cat bat rat")
    assert len(ws.placed_secret_words) == len(
        {word for word in ws.secret_words if word.direction}
    )


def test_random_words_only():
    ws: WordSearch = WordSearch()
    ws.random_words(5)
    assert len(ws.words) > 0


def test_random_words_added():
    ws: WordSearch = WordSearch("dog cat rat", size=25)
    ws.random_words(2, "ADD")
    assert len(ws.words) > 3


def test_random_words_count_type_error():
    ws: WordSearch = WordSearch()
    with pytest.raises(TypeError):
        ws.random_words("five")  # type: ignore


def test_random_words_count_value_error():
    ws: WordSearch = WordSearch()
    with pytest.raises(ValueError):
        ws.random_words(500)


def test_random_words_action_type_error():
    ws: WordSearch = WordSearch()
    with pytest.raises(TypeError):
        ws.random_words(5, action=5)  # type: ignore


def test_random_words_action_value_error():
    ws: WordSearch = WordSearch()
    with pytest.raises(ValueError):
        ws.random_words(5, "SUBTRACT")


def test_invalid_size_at_init_value():
    with pytest.raises(ValueError):
        ws: WordSearch = WordSearch(size=250)  # noqa: F841


def test_invalid_size_at_init_type():
    with pytest.raises(TypeError):
        ws: WordSearch = WordSearch(size="250")  # type: ignore  # noqa: F841


@pytest.mark.repeat(10)
def test_puzzle_solution_output(builtin_mask_shapes, capsys):
    ws: WordSearch = WordSearch(size=random.randint(21, 35))
    ws.random_words(random.randint(5, 21))
    mask_class: type[Mask] = random.choice(list(builtin_mask_shapes.values()))
    mask: Mask = mask_class()
    if mask:
        ws.apply_mask(mask)
    ws.formatter.CONSOLE = Console(color_system="truecolor", force_terminal=True)  # type: ignore[union-attr]
    ws.show(solution=True)

    captured = capsys.readouterr()
    stdout = captured.out
    stderr = captured.err

    assert not stderr
    assert "\x1b[" in stdout
    assert all(
        word.rich_style._make_ansi_codes(ColorSystem.TRUECOLOR) in stdout
        for word in ws.placed_words
    )


def test_unplaced_words():
    ws: WordSearch = WordSearch("dog", size=5)
    ws.add_words("generator")
    ws.add_words("refrigerator", secret=True)
    assert len(ws.unplaced_words) == 2


def test_unplaced_hidden_words():
    ws: WordSearch = WordSearch("dog", size=5)
    ws.add_words("generator")
    assert len(ws.unplaced_hidden_words) == 1


def test_unplaced_secret_words():
    ws: WordSearch = WordSearch("dog", size=5)
    ws.add_words("generator", secret=True)
    assert len(ws.unplaced_secret_words) == 1


def test_invalid_export_format(ws: WordSearch):
    with pytest.raises(ValueError):
        ws.save("test.pdf", format="GIF")


def test_missing_word_error():
    ws: WordSearch = WordSearch("dog", size=5, require_all_words=True)
    with pytest.raises(MissingWordError):
        ws.add_words("generator")


def test_cropped_puzzle_height(words):
    size = 21
    ws: WordSearch = WordSearch(words, size=size)
    assert len(ws.cropped_puzzle) == size


def test_cropped_puzzle_width(words):
    size = 21
    ws: WordSearch = WordSearch(words, size=size)
    assert len(ws.cropped_puzzle[0]) == size


def test_cropped_puzzle_masked_1(words):
    size = 20
    ws: WordSearch = WordSearch(words, size=size)
    ws.apply_mask(Rectangle(size - 2, size - 2, (1, 1)))
    assert ws.puzzle[1][1] == ws.cropped_puzzle[0][0]
    assert ws.puzzle[size - 2][size - 2] == ws.cropped_puzzle[size - 3][size - 3]


def test_cropped_puzzle_size(words):
    size = 20
    ws: WordSearch = WordSearch(words, size=size)
    rec_w = size - 5
    rec_h = size - 7
    ws.apply_mask(Rectangle(rec_w, rec_h, (1, 1)))
    w, h = ws.cropped_size
    assert w != ws.size
    assert h != ws.size
    assert ws.cropped_size == (rec_w, rec_h)


def test_cropped_puzzle_masked_2(words):
    size = 20
    ws: WordSearch = WordSearch(words, size=size)
    ws.apply_mask(Rectangle(size - 10, size - 10, (1, 1)))
    assert ws.puzzle[1][1] == ws.cropped_puzzle[0][0]
    assert ws.puzzle[size - 10][size - 10] == ws.cropped_puzzle[size - 11][size - 11]


@pytest.mark.repeat(10)
def test_word_placement(builtin_mask_shapes):
    def check_chars(puzzle, word):
        row, col = word.position
        for c in word.text:
            if c != puzzle[row][col]:
                return False
            row += word.direction.r_move
            col += word.direction.c_move
        return True

    ws: WordSearch = WordSearch(size=random.randint(21, 35))
    ws.random_words(random.randint(5, 21))
    mask_class: type[Mask] = random.choice(list(builtin_mask_shapes.values()))
    mask: Mask = mask_class()
    if mask:
        ws.apply_mask(mask)
    assert all(check_chars(ws.puzzle, word) for word in ws.placed_words)


def test_puzzle_size_error():
    ws: WordSearch = WordSearch("abracadabra")
    with pytest.raises(PuzzleSizeError):
        ws.size = 5


@pytest.mark.repeat(10)
def test_hide_fillers(builtin_mask_shapes):
    ws: WordSearch = WordSearch(size=random.randint(21, 35))
    ws.random_words(random.randint(5, 21))
    mask_class: type[Mask] = random.choice(list(builtin_mask_shapes.values()))
    mask: Mask = mask_class()
    if mask:
        ws.apply_mask(mask)
    hidden_fillers = formatter.hide_filler_characters(ws)
    chars: set[str] = set()
    for word in ws.placed_words:
        chars.update(hidden_fillers[y][x] for y, x in word.coordinates)
    assert " " not in chars


@pytest.mark.repeat(10)
def test_solution_plus_hide_fillers(builtin_mask_shapes):
    ws: WordSearch = WordSearch(size=random.randint(21, 35))
    ws.random_words(random.randint(5, 21))
    mask_class: type[Mask] = random.choice(list(builtin_mask_shapes.values()))
    mask: Mask = mask_class()
    if mask:
        ws.apply_mask(mask)
    chars = {c for chars in ws.puzzle for c in chars}
    assert "\x1b" not in chars


def test_word_directions(words, secret_words):
    """
    Hidden words can go NE, E, SE, or S.
    Secret words go on diagonals.
    Do they all obey the restriction rules?
    """
    ws: WordSearch = WordSearch(words, secret_words=secret_words, secret_level=7)
    assert all(w.direction in ws.directions for w in ws.placed_hidden_words)
    assert all(w.direction in ws.secret_directions for w in ws.placed_secret_words)


def test_validator_setter(words):
    ws: WordSearch = WordSearch(words, validators=None)
    ws.validators = [NoSingleLetterWords()]
    assert all(isinstance(v, NoSingleLetterWords) for v in ws.validators)  # type: ignore[union-attr]


def test_validator_setter_invalid_validator(words):
    class Val:
        pass

    with pytest.raises(TypeError):
        WordSearch(words, validators=[Val()])  # type: ignore[list-item]


def test_no_words_to_generate(ws: WordSearch):
    ws._words = WordSet()
    with pytest.raises(EmptyWordlistError):
        ws.generate()


def test_word_order_preservation():
    """Test that words maintain their original insertion order."""
    # Test with non-alphabetical order
    words = "zebra,apple,python,banana,xray,cherry,moon,date,ocean,forest"
    ws: WordSearch = WordSearch(words)

    # Extract word texts in order
    word_texts = [word.text for word in ws.words]
    expected_order = [
        "ZEBRA",
        "APPLE",
        "PYTHON",
        "BANANA",
        "XRAY",
        "CHERRY",
        "MOON",
        "DATE",
        "OCEAN",
        "FOREST",
    ]

    # Verify order is preserved (not alphabetical)
    assert word_texts == expected_order
    assert word_texts != sorted(word_texts)  # Confirm it's not alphabetical


def test_word_order_preservation_with_operations():
    """Test that word order is preserved through various operations."""
    # Start with some words
    ws: WordSearch = WordSearch("first,second")

    # Add more words
    ws.add_words("third,fourth")
    word_texts = [word.text for word in ws.words]
    assert word_texts == ["FIRST", "SECOND", "THIRD", "FOURTH"]

    # Test hidden vs secret words maintain separate order
    ws2 = WordSearch("regular1,regular2", secret_words="secret1,secret2")
    hidden_texts = [word.text for word in ws2.hidden_words]
    secret_texts = [word.text for word in ws2.secret_words]

    assert hidden_texts == ["REGULAR1", "REGULAR2"]
    assert secret_texts == ["SECRET1", "SECRET2"]


def test_word_order_preservation_placed_words():
    """Test that placed words maintain order."""
    words = "cat,dog,bird,fish,mouse"
    ws: WordSearch = WordSearch(words)
    ws.generate()

    # Get placed words in order
    placed_texts = [word.text for word in ws.placed_words]
    original_texts = [word.text for word in ws.words]

    # Placed words should be a subset in the same relative order
    placed_index = 0
    for word_text in original_texts:
        if placed_index < len(placed_texts) and word_text == placed_texts[placed_index]:
            placed_index += 1

    # All placed words should have been found in order
    assert placed_index == len(placed_texts)


def test_word_search_show_with_sorting(capsys):
    """Test WordSearch.show() with default sorting behavior."""
    ws: WordSearch = WordSearch("zebra,apple,cat")
    ws.show(sort_word_list=True)

    # Capture the printed output
    captured = capsys.readouterr()
    # Check that words appear in alphabetical order in output
    assert "APPLE, CAT, ZEBRA" in captured.out


def test_word_search_show_without_sorting(capsys):
    """Test WordSearch.show() with sorting disabled."""
    ws: WordSearch = WordSearch("zebra,apple,cat")
    ws.show(sort_word_list=False)

    # Capture the printed output
    captured = capsys.readouterr()
    # Check that words appear in original order in output
    assert "ZEBRA, APPLE, CAT" in captured.out


def test_word_search_save_csv_with_sorting(tmp_path):
    """Test WordSearch.save() CSV format with sorting."""
    ws: WordSearch = WordSearch("zebra,apple,cat")
    csv_file = tmp_path / "test_sorted.csv"

    ws.save(csv_file, format="CSV", sort_word_list=True)
    assert csv_file.exists()

    content = csv_file.read_text()
    lines = content.split("\n")

    # Find the word list line
    word_line = None
    for line in lines:
        if "APPLE" in line and "ZEBRA" in line and "CAT" in line:
            word_line = line
            break

    assert word_line is not None
    # Should be in alphabetical order
    apple_pos = word_line.find("APPLE")
    cat_pos = word_line.find("CAT")
    zebra_pos = word_line.find("ZEBRA")
    assert apple_pos < cat_pos < zebra_pos


def test_word_search_save_csv_without_sorting(tmp_path):
    """Test WordSearch.save() CSV format without sorting."""
    ws: WordSearch = WordSearch("zebra,apple,cat")
    csv_file = tmp_path / "test_unsorted.csv"

    ws.save(csv_file, format="CSV", sort_word_list=False)
    assert csv_file.exists()

    content = csv_file.read_text()
    lines = content.split("\n")

    # Find the word list line
    word_line = None
    for line in lines:
        if "APPLE" in line and "ZEBRA" in line and "CAT" in line:
            word_line = line
            break

    assert word_line is not None
    # Should be in original order
    zebra_pos = word_line.find("ZEBRA")
    apple_pos = word_line.find("APPLE")
    cat_pos = word_line.find("CAT")
    assert zebra_pos < apple_pos < cat_pos


def test_word_search_save_json_with_sorting(tmp_path):
    """Test WordSearch.save() JSON format with sorting."""
    ws: WordSearch = WordSearch("dog,cat,bat")
    json_file = tmp_path / "test_sorted.json"

    ws.save(json_file, format="JSON", sort_word_list=True)
    assert json_file.exists()

    import json

    with open(json_file) as f:
        data = json.load(f)

    words = data.get("words", [])
    # Should contain all words
    assert len(words) == 3
    # Words should be present (order in JSON might depend on how words were placed)
