from pathlib import Path

import pytest

from word_search_generator import WordSearch
from word_search_generator.game import (
    Game,
    MissingFormatterError,
    MissingGeneratorError,
)
from word_search_generator.generator import WordSearchGenerator


def test_valid_cleanup_input_with_spaces(ws: WordSearch):
    word_list = ["cat", "bird", "pig", "horse"]
    words = ws.cleanup_input(" ".join(word_list))
    assert len(words) == len(word_list)


def test_valid_cleanup_input_with_commas(ws: WordSearch):
    word_list = ["cat", "bird", "pig", "horse"]
    words = ws.cleanup_input(",".join(word_list))
    assert len(words) == len(word_list)


def test_invalid_cleanup_input(ws: WordSearch):
    with pytest.raises(TypeError):
        ws.cleanup_input(1)  # type: ignore


def test_invalid_level_direction_type(ws: WordSearch):
    with pytest.raises(TypeError):
        ws.validate_level(None)


def test_missing_generator():
    with pytest.raises(MissingGeneratorError):
        game = Game("dog cat horse")  # noqa: F841


def test_missing_generator_during_generate_method(words):
    ws = WordSearch()
    ws.generator = None
    assert ws.generator != ws.DEFAULT_GENERATOR
    ws.add_words(words)
    assert ws.generator == ws.DEFAULT_GENERATOR


def test_missing_default_generator_str_repr(ws: WordSearch):
    ws.generator = ws.DEFAULT_GENERATOR = None  # type: ignore[assignment]
    with pytest.raises(MissingGeneratorError):
        ws.__str__()


def test_missing_formatter():
    game = Game("dog cat horse", generator=WordSearchGenerator())
    with pytest.raises(MissingFormatterError):
        game.show()


def test_missing_formatter_during_show_method(ws: WordSearch):
    ws.formatter = None
    ws.show()
    assert ws.formatter == ws.DEFAULT_FORMATTER


def test_missing_formatter_during_save_method(ws: WordSearch, tmp_path: Path):
    ws.formatter = None
    assert ws.formatter != ws.DEFAULT_FORMATTER
    path = tmp_path.joinpath("test.json")
    ws.save(path, "JSON")
    assert ws.formatter == ws.DEFAULT_FORMATTER


def test_missing_default_formatter_in_str_repr(ws: WordSearch):
    ws.formatter = ws.DEFAULT_FORMATTER = None  # type: ignore[assignment]
    with pytest.raises(MissingFormatterError):
        ws.__str__()


def test_missing_default_formatter(tmp_path: Path):
    game = Game("dog cat horse", generator=WordSearchGenerator())
    game.formatter = game.DEFAULT_FORMATTER = None  # type: ignore[assignment]
    with pytest.raises(MissingFormatterError):
        game.save(tmp_path.joinpath("hey-yo.pdf"))
