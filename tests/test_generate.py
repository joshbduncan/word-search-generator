from word_search_generator.generate import check_for_dupes_at_position


def test_dupe_at_position_1():
    placed_words = ["BAT", "CAT", "RAT"]
    puzzle = [
        ["B", "•", "•", "•", "R"],
        ["•", "A", "•", "•", "A"],
        ["•", "•", "T", "•", "T"],
        ["•", "•", "•", "•", "•"],
        ["C", "A", "T", "•", "B"],
    ]
    check = check_for_dupes_at_position(puzzle, "A", (3, 3), placed_words)
    print(f"{check=}")
    assert check is False


def test_dupe_at_position_2():
    placed_words = ["BAT", "CAT", "RAT"]
    puzzle = [
        ["B", "•", "•", "•", "R"],
        ["•", "A", "•", "•", "A"],
        ["•", "•", "T", "•", "T"],
        ["•", "•", "•", "•", "•"],
        ["C", "A", "T", "•", "B"],
    ]
    check = check_for_dupes_at_position(puzzle, "A", (1, 3), placed_words)
    print(f"{check=}")
    assert check is False
