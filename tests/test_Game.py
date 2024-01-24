from pathlib import Path

import pytest

from word_search_generator import WordSearch
from word_search_generator.core.directions import LEVEL_DIRS
from word_search_generator.core.game import (
    Game,
    MissingFormatterError,
    MissingGeneratorError,
)
from word_search_generator.core.word import Direction, Word
from word_search_generator.word_search._generator import WordSearchGenerator


def test_empty_object(empty_game: Game):
    assert len(empty_game.words) == 0


@pytest.mark.parametrize(
    "level,expected",
    [
        (1, LEVEL_DIRS[1]),
        (2, LEVEL_DIRS[2]),
        (3, LEVEL_DIRS[3]),
        (4, LEVEL_DIRS[4]),
        (5, LEVEL_DIRS[5]),
        (7, LEVEL_DIRS[7]),
        (8, LEVEL_DIRS[8]),
        ("n", Direction.N),
        ("NE", Direction.NE),
        ("e", Direction.E),
        ("SE", Direction.SE),
        ("s", Direction.S),
        ("SW", Direction.SW),
        ("w", Direction.W),
        ("NW", Direction.NW),
    ],
)
def test_set_puzzle_level(level: int | str, expected: set[Direction]):
    g = Game(level=level)
    g.directions == expected


@pytest.mark.parametrize(
    "level,expected",
    [
        (1, LEVEL_DIRS[1]),
        (2, LEVEL_DIRS[2]),
        (3, LEVEL_DIRS[3]),
        (4, LEVEL_DIRS[4]),
        (5, LEVEL_DIRS[5]),
        (7, LEVEL_DIRS[7]),
        (8, LEVEL_DIRS[8]),
        ("n", Direction.N),
        ("NE", Direction.NE),
        ("e", Direction.E),
        ("SE", Direction.SE),
        ("s", Direction.S),
        ("SW", Direction.SW),
        ("w", Direction.W),
        ("NW", Direction.NW),
    ],
)
def test_set_secret_level(words, level: int, expected: set[Direction]):
    ws = WordSearch(words)
    ws.secret_directions = level  # type: ignore[assignment]
    ws.directions == expected


@pytest.mark.parametrize(
    "level,expected_exception",
    [
        (757, ValueError),
        ("A", TypeError),
        (17.75, TypeError),
        ("", TypeError),
        (-2, ValueError),
    ],
)
def test_invalid_puzzle_level(empty_game: Game, level, expected_exception):
    with pytest.raises(expected_exception):
        empty_game.level = level


def test_manual_level_control(ws: WordSearch):
    tst_dirs = {Direction.E, Direction.SW, (-1, 0)}
    ws.directions = tst_dirs  # type: ignore
    assert ws.directions == ws.validate_level(tst_dirs)


@pytest.mark.parametrize(
    "size,expected_size",
    [
        (Game.MIN_PUZZLE_SIZE, Game.MIN_PUZZLE_SIZE),
        (15, 15),
        (25, 25),
        (Game.MAX_PUZZLE_SIZE, Game.MAX_PUZZLE_SIZE),
    ],
)
def test_puzzle_size(ws: WordSearch, size: int, expected_size: int):
    ws.size = size
    assert ws.size == size
    assert len(ws.puzzle) == expected_size


@pytest.mark.parametrize(
    "size,expected_size",
    [
        (1, ValueError),
        ("A", TypeError),
        (17.75, TypeError),
        ("", TypeError),
        (-2, ValueError),
    ],
)
def test_invalid_puzzle_size(ws: WordSearch, size, expected_size):
    with pytest.raises(expected_size):
        ws.size = size


@pytest.mark.parametrize(
    "words,ct",
    [
        ("cat bird pig horse", 4),
        ("cat,bird,pig,horse", 4),
        ("cat\nbird\npig\nhorse", 4),
        ("cat bird, pig\nhorse", 4),
        ("cat               bird,\n\n\n\npig,,   ,,, horse", 4),
    ],
)
def test_cleanup_input(ws: WordSearch, words: str, ct: int):
    assert len(ws._cleanup_input(words, False, max_words=50)) == ct


def test_invalid_cleanup_input(ws: WordSearch):
    with pytest.raises(TypeError):
        ws._cleanup_input(1, False, 10)  # type: ignore


def test_invalid_level_direction_type(ws: WordSearch):
    with pytest.raises(TypeError):
        ws.validate_level(None)


def test_missing_generator():
    with pytest.raises(MissingGeneratorError):
        game = Game("dog cat horse")  # noqa: F841


@pytest.mark.parametrize(
    "words,expected",
    [
        ("test", ["test"]),
        ("hey", ["hey"]),
        ("a long list of words", ["long", "list", "of", "words"]),
        ("a b c d me e f g", ["me"]),
    ],
)
def test_add_words(ws: WordSearch, words: str, expected):
    ws.add_words(words)
    assert all(Word(word) in ws.words for word in expected)


def test_add_regular_words_replacing_secret_word(ws: WordSearch):
    ws.add_words("test", True)
    ws.add_words("test")
    assert Word("test") not in ws.secret_words and Word("test") in ws.words


@pytest.mark.parametrize(
    "words,expected",
    [
        ("test", ["test"]),
        ("hey", ["hey"]),
        ("a long list of words", ["long", "list", "of", "words"]),
        ("a b c d me e f g", ["me"]),
    ],
)
def test_add_secret_words(ws: WordSearch, words: str, expected):
    ws.add_words(words, secret=True)
    assert all(Word(word) in ws.secret_words for word in expected)


def test_add_secret_words_replacing_regular_word(ws: WordSearch):
    ws.add_words("test")
    ws.add_words("test", True)
    assert Word("test") not in ws.hidden_words and Word("test") in ws.secret_words


@pytest.mark.parametrize(
    "words,word",
    [
        ("bird cat dog horse pig", "cat"),
        ("bird cat dog horse pig", "bird"),
        ("bird cat dog horse pig", "pig"),
    ],
)
def test_remove_words(ws: WordSearch, words: str, word: str):
    ws.add_words(f"{words}")
    ws.remove_words(word)
    assert Word(word) not in ws.words


@pytest.mark.parametrize(
    "words,word",
    [
        ("bird cat dog horse pig", "cat"),
        ("bird cat dog horse pig", "bird"),
        ("bird cat dog horse pig", "pig"),
    ],
)
def test_remove_words_from_secret_words(ws: WordSearch, words: str, word: str):
    ws.add_words(words, secret=True)
    ws.remove_words(word)
    assert Word(word) not in ws.words.union(ws.secret_words)


@pytest.mark.parametrize(
    "words,ct",
    [
        ("bird cat dog horse pig", 5),
        ("bird", 1),
        ("bird cat dog horse pig cup can laptop glasses", 9),
    ],
)
def test_replace_words(words: str, ct: int):
    ws = WordSearch("word puzzle game")
    assert len(ws.words) == 3
    ws.replace_words(words)
    assert len(ws.words) == ct


@pytest.mark.parametrize(
    "words,ct",
    [
        ("bird cat dog horse pig", 5),
        ("bird", 1),
        ("bird cat dog horse pig cup can laptop glasses", 9),
    ],
)
def test_replace_secret_words(words: str, ct: int):
    ws = WordSearch("word puzzle game", secret_words="secret, blind, nope")
    ws.replace_words(words, True)
    assert len(ws.secret_words) == ct


def test_missing_generator_during_generate_method(words):
    ws = WordSearch()
    ws.generator = None
    assert ws.generator != ws.DEFAULT_GENERATOR
    ws.add_words(words)
    assert ws.generator == ws.DEFAULT_GENERATOR


def test_missing_formatter(words):
    game = Game(words, generator=WordSearchGenerator())
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


def test_missing_default_formatter(tmp_path: Path):
    game = Game("dog cat horse", generator=WordSearchGenerator())
    game.formatter = game.DEFAULT_FORMATTER = None  # type: ignore[assignment]
    with pytest.raises(MissingFormatterError):
        game.save(tmp_path.joinpath("hey-yo.pdf"))


def test_empty_puzzle_str(empty_game: Game):
    assert str(empty_game) == "Empty puzzle."


def test_invalid_validator_iterable(empty_game: Game):
    with pytest.raises(TypeError):
        empty_game.validators = "cat"  # type: ignore


def test_invalid_validator(empty_game: Game):
    with pytest.raises(TypeError):
        empty_game.validators = ["cat"]  # type: ignore
