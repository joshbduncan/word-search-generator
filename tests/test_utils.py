import pytest

from word_search_generator import WordSearch, utils
from word_search_generator.word import Word


def test_valid_cleanup_input_with_spaces():
    word_list = ["cat", "bird", "pig", "horse"]
    words = utils.cleanup_input(" ".join(word_list))
    assert len(words) == len(word_list)


def test_valid_cleanup_input_with_commas():
    word_list = ["cat", "bird", "pig", "horse"]
    words = utils.cleanup_input(",".join(word_list))
    assert len(words) == len(word_list)


def test_invalid_cleanup_input():
    with pytest.raises(TypeError):
        utils.cleanup_input(1)  # type: ignore


def test_invalid_input_too_short():
    with pytest.raises(ValueError):
        utils.cleanup_input("a")


def test_stringify():
    inp = [["a"], ["b"], ["c"]]
    output = "a\nb\nc"
    assert utils.stringify(inp, ((0, 0), (1, 3))) == output


def test_palindromes():
    assert utils.is_palindrome("level")


def test_word_within_word():
    words = set()
    for word in ["rain", "sun", "clouds"]:
        words.add(Word(word))
    assert utils.word_contains_word(words, "")


def test_invalid_level_direction_type():
    with pytest.raises(TypeError):
        utils.validate_level(None)


def test_answer_key_list():
    p = WordSearch("bat cab rat")
    key_as_list = utils.get_answer_key_list(
        p.hidden_words.union(p.secret_words), p.bounding_box
    )
    assert len(key_as_list) == len(p.key) and key_as_list[0].startswith("BAT")
