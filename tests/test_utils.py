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
