from word_search_generator import WordSearch
from word_search_generator.generate import no_duped_words
from word_search_generator.types import Position
from word_search_generator.utils import get_random_words


def test_dupe_at_position_1():
    puzzle = WordSearch("bat cab rat", size=5)
    puzzle._key = {
        "BAT": {
            "start": Position(0, 0),
            "direction": "SE",
            "secret": False,
        },
        "CAB": {
            "start": Position(4, 2),
            "direction": "SE",
            "secret": False,
        },
        "RAT": {
            "start": Position(0, 4),
            "direction": "S",
            "secret": False,
        },
    }
    puzzle._solution = puzzle._puzzle = [
        ["B", "", "", "", "R"],
        ["", "A", "", "", "A"],
        ["", "", "T", "", "T"],
        ["", "", "", "", ""],
        ["", "", "C", "A", "B"],
    ]
    check = no_duped_words(puzzle, "A", (3, 3))
    assert check is False


def test_dupe_at_position_2():
    puzzle = WordSearch("bat cab rat", size=5)
    puzzle._key = {
        "BAT": {
            "start": Position(0, 0),
            "direction": "SE",
            "secret": False,
        },
        "CAB": {
            "start": Position(4, 2),
            "direction": "SE",
            "secret": False,
        },
        "RAT": {
            "start": Position(0, 4),
            "direction": "S",
            "secret": False,
        },
    }
    puzzle._solution = puzzle._puzzle = [
        ["B", "", "", "", "R"],
        ["", "A", "", "", "A"],
        ["", "", "T", "", "T"],
        ["", "", "", "", ""],
        ["", "", "C", "A", "B"],
    ]
    check = no_duped_words(puzzle, "A", (1, 3))
    assert check is False


def test_no_dupe_at_position():
    puzzle = WordSearch("bat cab rat", size=5)
    puzzle._key = {
        "BAT": {
            "start": Position(0, 0),
            "direction": "SE",
            "secret": False,
        },
        "CAB": {
            "start": Position(4, 2),
            "direction": "SE",
            "secret": False,
        },
        "RAT": {
            "start": Position(0, 4),
            "direction": "S",
            "secret": False,
        },
    }
    puzzle._solution = puzzle._puzzle = [
        ["B", "", "", "", "R"],
        ["", "A", "", "", "A"],
        ["", "", "T", "", "T"],
        ["", "", "", "", ""],
        ["", "", "C", "A", "B"],
    ]
    check = no_duped_words(puzzle, "Z", (1, 3))
    assert check is True


def test_puzzle_size_less_than_shortest_word_length():
    p = WordSearch("DONKEY", size=5)
    assert p.size == 7


def test_only_placed_words_in_key():
    w = get_random_words(100)
    p = WordSearch(w, size=5)
    assert all(word.direction for word in p.placed_words)


def test_too_many_supplied_words():
    w = get_random_words(100)
    p = WordSearch(w, size=5)
    assert len(p.words) != len(p.placed_words)
