from word_search_generator.config import level_dirs, max_puzzle_words
from word_search_generator.game.word_search import WordSearch
from word_search_generator.generator import WordSearchGenerator
from word_search_generator.utils import calc_puzzle_size, get_random_words


def test_dupe_at_position_1(generator_test_puzzle, placed_words):
    gen = WordSearchGenerator()
    gen.puzzle = generator_test_puzzle
    gen.words = placed_words
    check = gen.no_duped_words("A", (3, 3))
    assert check is False


def test_dupe_at_position_2(generator_test_puzzle, placed_words):
    gen = WordSearchGenerator()
    gen.puzzle = generator_test_puzzle
    gen.words = placed_words
    check = gen.no_duped_words("A", (1, 3))
    assert check is False


def test_no_dupe_at_position(generator_test_puzzle, placed_words):
    gen = WordSearchGenerator()
    gen.puzzle = generator_test_puzzle
    gen.words = placed_words
    check = gen.no_duped_words("Z", (1, 3))
    assert check is True


def test_only_placed_words_in_key(ws):
    assert all(word.direction for word in ws.placed_words)


def test_too_many_supplied_words():
    w = ",".join(get_random_words(25))
    ws = WordSearch(w, size=5)
    assert len(ws.words) != len(ws.placed_words)


def test_fit_all_words_with_plenty_of_space():
    for _ in range(10):
        ws = WordSearch("cat dog pig cow mule duck")
        assert len(ws.placed_words) == 6


def test_fit_all_words_with_plenty_of_space_and_secret_words():
    for _ in range(10):
        ws = WordSearch("cat dog pig", secret_words="cow mule duck")
        assert len(ws.placed_words) == 6


def test_too_many_words():
    ws = WordSearch(size=50)
    ws.random_words(100)
    ws.random_words(100, action="ADD")
    assert len(ws.placed_words) <= max_puzzle_words


def test_too_many_secret_words():
    ws = WordSearch(size=50)
    ws.random_words(100)
    ws.random_words(100, action="ADD", secret=True)
    assert len(ws.placed_words) <= max_puzzle_words


def test_secret_word_directions():
    words = "cat bat rat"
    level = 1  # right or down
    secret_words = "pig dog fox"
    secret_level = 7  # diagonals only
    ws = WordSearch(
        words, level=level, secret_words=secret_words, secret_level=secret_level
    )
    for w in ws.placed_secret_words:
        assert w.direction in level_dirs[secret_level]


def test_generated_size(words):
    ws = WordSearch(words)
    calculated_size = calc_puzzle_size(ws.words, ws.level)
    assert calculated_size == ws.size
