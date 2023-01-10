from word_search_generator import WordSearch
from word_search_generator.config import max_puzzle_words
from word_search_generator.generate import no_duped_words
from word_search_generator.utils import get_random_words
from word_search_generator.word import Direction, Word, Wordlist


def setup_words():
    BAT = Word("bat")
    BAT.start_row = 0
    BAT.start_column = 0
    BAT.direction = Direction.SE
    BAT.secret = False
    PLACED_WORDS.add(BAT)

    CAB = Word("cab")
    CAB.start_row = 4
    CAB.start_column = 2
    CAB.direction = Direction.SE
    CAB.secret = False
    PLACED_WORDS.add(CAB)

    RAT = Word("rat")
    RAT.start_row = 0
    RAT.start_column = 4
    RAT.direction = Direction.S
    RAT.secret = False
    PLACED_WORDS.add(RAT)


PLACED_WORDS: Wordlist = set()
setup_words()
PUZZLE = [
    ["B", "", "", "", "R"],
    ["", "A", "", "", "A"],
    ["", "", "T", "", "T"],
    ["", "", "", "", ""],
    ["", "", "C", "A", "B"],
]


def test_dupe_at_position_1():
    check = no_duped_words(PUZZLE, {word.text for word in PLACED_WORDS}, "A", (3, 3))
    assert check is False


def test_dupe_at_position_2():
    check = no_duped_words(PUZZLE, {word.text for word in PLACED_WORDS}, "A", (1, 3))
    assert check is False


def test_no_dupe_at_position():
    check = no_duped_words(PUZZLE, {word.text for word in PLACED_WORDS}, "Z", (1, 3))
    assert check is True


def test_puzzle_size_less_than_shortest_word_length():
    ws = WordSearch("DONKEY", size=5)
    assert ws.size == 7


def test_only_placed_words_in_key():
    w = ",".join(get_random_words(100))
    p = WordSearch(w, size=5)
    assert all(word.direction for word in p.placed_words)


def test_too_many_supplied_words():
    w = ",".join(get_random_words(100))
    p = WordSearch(w, size=5)
    assert len(p.words) != len(p.placed_words)


def test_fit_all_words_with_plenty_of_space():
    for _ in range(10):
        p = WordSearch("cat dog pig cow mule duck")
        assert len(p.placed_words) == 6


def test_fit_all_words_with_plenty_of_space_and_secret_words():
    for _ in range(10):
        p = WordSearch("cat dog pig", secret_words="cow mule duck")
        assert len(p.placed_words) == 6


def test_too_many_words():
    p = WordSearch(size=50)
    p.random_words(100)
    p.random_words(100, action="ADD")
    assert len(p.placed_words) <= max_puzzle_words


def test_too_many_secret_words():
    p = WordSearch(size=50)
    p.random_words(100)
    p.random_words(100, action="ADD", secret=True)
    assert len(p.placed_words) <= max_puzzle_words
