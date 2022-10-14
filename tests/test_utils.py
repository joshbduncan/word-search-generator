import pytest

from word_search_generator import utils


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
    assert utils.stringify(inp) == output


def test_palindromes():
    assert utils.is_palindrome("level")


def test_word_within_word():
    assert utils.word_contains_word({"rain", "sun", "clouds"}, "")


def test_invalid_level_direction_type():
    with pytest.raises(TypeError):
        utils.validate_level(None)
