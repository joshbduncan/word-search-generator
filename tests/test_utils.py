import pytest

from word_search_generator import utils
from word_search_generator.types import KeyInfo, Position


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


def test_answer_key_list():
    key = {}
    key["BAT"] = KeyInfo(
        {"start": Position(row=0, column=0), "direction": "SE", "secret": False}
    )
    key["CAB"] = KeyInfo(
        {"start": Position(row=4, column=2), "direction": "SE", "secret": False}
    )
    key["RAT"] = KeyInfo(
        {"start": Position(row=0, column=4), "direction": "S", "secret": True}
    )
    key_as_list = utils.get_answer_key_list(key)
    assert len(key_as_list) == len(key) and key_as_list[0].startswith("BAT")
