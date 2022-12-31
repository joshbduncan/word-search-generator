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
    inp = [
        ["a", "a", "a", "a", "a", "a"],
        ["b", "b", "b", "b", "b", "b"],
        ["c", "c", "c", "c", "c", "c"],
        ["d", "d", "d", "d", "d", "d"],
        ["e", "e", "e", "e", "e", "e"],
        ["f", "f", "f", "f", "f", "f"],
    ]
    output = (
        "a a a a a a\nb b b b b b\nc c c c c c\nd d d d d d\ne e e e e e\nf f f f f f"
    )
    assert utils.stringify(inp, ((0, 0), (6, 6))) == output


def test_stringify_offset():
    inp = [
        ["a", "a", "a", "a", "a"],
        ["b", "b", "b", "b", "b"],
        ["c", "c", "c", "c", "c"],
        ["d", "d", "d", "d", "d"],
        ["e", "e", "e", "e", "e"],
    ]
    output = " a a a a a\n b b b b b\n c c c c c\n d d d d d\n e e e e e"
    assert utils.stringify(inp, ((0, 0), (4, 4))) == output


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


def test_float_range():
    assert len(list(utils.float_range(0.10))) == 1


def test_float_range_invalid_args():
    assert not list(utils.float_range(0.40, 0.10, 0.01))


def test_float_range_negative():
    assert len(list(utils.float_range(0.40, 0.30, -0.1))) == 2
