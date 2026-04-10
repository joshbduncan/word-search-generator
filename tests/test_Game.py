import json
from pathlib import Path

import pytest
from ordered_set import OrderedSet

from word_search_generator import WordSearch
from word_search_generator.core import Formatter, Game, Generator
from word_search_generator.core.directions import LEVEL_DIRS
from word_search_generator.core.game import (
    EmptyPuzzleError,
    EmptyWordlistError,
    MissingFormatterError,
    MissingGeneratorError,
    MissingWordError,
    PuzzleSizeError,
)
from word_search_generator.core.word import Direction, Word
from word_search_generator.word_search._generator import WordSearchGenerator


def test_empty_object(empty_game: Game):
    assert len(empty_game.words) == 0


@pytest.mark.parametrize(
    "level,expected",
    [
        (1, set(LEVEL_DIRS[1])),
        (2, set(LEVEL_DIRS[2])),
        (3, set(LEVEL_DIRS[3])),
        (4, set(LEVEL_DIRS[4])),
        (5, set(LEVEL_DIRS[5])),
        (7, set(LEVEL_DIRS[7])),
        (8, set(LEVEL_DIRS[8])),
        ("n", {Direction.N}),
        ("NE", {Direction.NE}),
        ("e", {Direction.E}),
        ("SE", {Direction.SE}),
        ("s", {Direction.S}),
        ("SW", {Direction.SW}),
        ("w", {Direction.W}),
        ("NW", {Direction.NW}),
    ],
)
def test_set_puzzle_level(
    empty_generator: Generator,
    empty_formatter: Formatter,
    level: int | str,
    expected: set[Direction],
):
    words = OrderedSet([Word("dog"), Word("cat"), Word("horse")])
    g = Game(
        words=words, level=level, generator=empty_generator, formatter=empty_formatter
    )
    assert g.directions == expected


@pytest.mark.parametrize(
    "level,expected",
    [
        (1, set(LEVEL_DIRS[1])),
        (2, set(LEVEL_DIRS[2])),
        (3, set(LEVEL_DIRS[3])),
        (4, set(LEVEL_DIRS[4])),
        (5, set(LEVEL_DIRS[5])),
        (7, set(LEVEL_DIRS[7])),
        (8, set(LEVEL_DIRS[8])),
        ("n", {Direction.N}),
        ("NE", {Direction.NE}),
        ("e", {Direction.E}),
        ("SE", {Direction.SE}),
        ("s", {Direction.S}),
        ("SW", {Direction.SW}),
        ("w", {Direction.W}),
        ("NW", {Direction.NW}),
    ],
)
def test_set_secret_level(words, level: int, expected: set[Direction]):
    ws = WordSearch(words)
    ws.secret_directions = level
    assert ws.secret_directions == expected


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
def test_cleanup_input(base_game: Game, words: str, ct: int):
    assert len(base_game._cleanup_input(words, False)) == ct
    with pytest.raises(TypeError):
        base_game._cleanup_input(["cat", "bat", "rat"])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        base_game._cleanup_input(1, False, 10)  # type: ignore


def test_invalid_level_direction_type(base_game: Game):
    with pytest.raises(TypeError):
        base_game.validate_level(None)  # type: ignore[arg-type]


def test_missing_generator():
    with pytest.raises(MissingGeneratorError):
        words = OrderedSet([Word("dog"), Word("cat"), Word("horse")])
        Game(words)


@pytest.mark.parametrize(
    "words,expected",
    [
        ("test", ["test"]),
        ("hey", ["hey"]),
        ("a long list of words", ["long", "list", "of", "words"]),
        ("a b c d me e f g", ["me"]),
    ],
)
def test_add_words(base_game: Game, words: str, expected):
    base_game.add_words(words)
    assert all(Word(word) in base_game.words for word in expected)


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
    with pytest.raises(MissingGeneratorError):
        ws.add_words(words)


def test_missing_formatter(tmp_path: Path):
    words = OrderedSet([Word("dog"), Word("cat"), Word("horse")])
    game = Game(words, generator=WordSearchGenerator())
    path = tmp_path.joinpath("test.pdf")
    with pytest.raises(MissingFormatterError):
        game.show()
    with pytest.raises(MissingFormatterError):
        game.save(path)


def test_missing_default_formatter(tmp_path: Path):
    words = OrderedSet([Word("dog"), Word("cat"), Word("horse")])
    game = Game(words, generator=WordSearchGenerator())
    game.formatter = game.DEFAULT_FORMATTER = (
        None  # ty:ignore[invalid-attribute-access]
    )
    with pytest.raises(MissingFormatterError):
        game.save(tmp_path.joinpath("hey-yo.pdf"))


def test_empty_puzzle_str(empty_game: Game):
    assert str(empty_game) == "Empty puzzle."


def test_json(base_game: Game):
    assert json.loads(base_game.json)["puzzle"] == base_game.puzzle


def test_json_empty_puzzle_error(base_game: Game):
    assert base_game
    base_game._puzzle = []
    with pytest.raises(EmptyPuzzleError):
        base_game.json  # noqa: B018


def test_empty_word_list_error(base_game: Game):
    assert base_game
    base_game._words = OrderedSet()
    with pytest.raises(EmptyWordlistError):
        base_game.generate()


def test_generate_puzzle_size_error():
    g = Game("cat bat eleven", size=5, generator=WordSearchGenerator())
    assert g
    with pytest.raises(PuzzleSizeError):
        g.replace_words("longggggg")


def test_require_all_words():
    with pytest.raises(MissingWordError):
        g = Game(  # noqa
            "cat bat eleven longggggg",
            size=5,
            require_all_words=True,
            generator=WordSearchGenerator(),
        )


def test_equality(words):
    g1 = Game(words, size=10, generator=WordSearchGenerator())
    g2 = Game(words, size=10, generator=WordSearchGenerator())
    assert g1 == g2


def test_puzzle_inequality(words):
    g1 = Game(words, size=10, generator=WordSearchGenerator())
    g2 = Game(words, size=10, generator=WordSearchGenerator())
    g2.add_words("vinegar")
    assert g1 != g2


def test_puzzle_inequality_diff_type(words):
    g = Game(words, size=10, generator=WordSearchGenerator())
    assert g != "cat"


def test_repr(base_game: Game):
    """Test that repr is informative and parameters can recreate equivalent games.

    The repr focuses on core puzzle characteristics (words, level, size) that
    define puzzle identity according to __eq__. It does not include implementation
    details like generator, formatter, or validators.
    """
    repr_str = repr(base_game)

    # Repr should contain the class name and key parameters
    assert "Game" in repr_str
    assert "words=" in repr_str
    assert "level=" in repr_str
    assert "size=" in repr_str

    # Repr should contain all word texts
    for word in base_game.words:
        assert word.text in repr_str

    # Create an equivalent game using the same parameters
    words_list = ",".join(word.text for word in base_game.words)
    equivalent_game = Game(
        words=words_list,
        level=",".join(d.name for d in base_game.directions),
        size=base_game.size,
        generator=base_game.generator,
        formatter=base_game.formatter,
        validators=base_game._validators,
    )

    # Should be equal according to __eq__ (compares words, directions, size)
    assert equivalent_game == base_game
