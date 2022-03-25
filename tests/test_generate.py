import pytest

from word_search_generator.generate import check_for_dupes_at_position


def test_dupe_at_position_1():
    words = {"CAT", "BAT", "RAT", "HAT", "MAT", "DONKEY"}
    puzzle = [
        ["B", "•", "•", "•", "•"],
        ["•", "A", "•", "•", "•"],
        ["•", "•", "T", "•", "•"],
        ["•", "•", "•", "•", "•"],
        ["•", "•", "•", "•", "B"],
    ]
    check = check_for_dupes_at_position(puzzle, "A", (3, 3), words)
    print(f"{check=}")
    assert check == False


def test_dupe_at_position_2():
    words = {"CAT", "BAT", "RAT", "HAT", "MAT", "DONKEY"}
    puzzle = [
        ["B", "•", "•", "•", "C"],
        ["•", "A", "•", "•", "•"],
        ["•", "•", "T", "•", "•"],
        ["•", "•", "•", "•", "•"],
        ["•", "•", "•", "•", "C"],
    ]
    check = check_for_dupes_at_position(puzzle, "A", (1, 3), words)
    print(f"{check=}")
    assert check == False
