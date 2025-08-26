import random

import pytest

from word_search_generator.utils import (
    float_range,
    get_answer_key_list,
    get_random_words,
    get_word_list_list,
    stringify,
)
from word_search_generator.words import WORD_LISTS


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
    assert stringify(inp, ((0, 0), (6, 6))) == output


def test_stringify_offset():
    inp = [
        ["a", "a", "a", "a", "a"],
        ["b", "b", "b", "b", "b"],
        ["c", "c", "c", "c", "c"],
        ["d", "d", "d", "d", "d"],
        ["e", "e", "e", "e", "e"],
    ]
    output = " a a a a a\n b b b b b\n c c c c c\n d d d d d\n e e e e e"
    assert stringify(inp, ((0, 0), (4, 4))) == output


def test_answer_key_list(ws, words):
    word_list = get_word_list_list(ws.words)
    key_as_list = get_answer_key_list(word_list, ws.bounding_box)
    assert len(key_as_list) == len(ws.key)


def test_float_range():
    assert len(list(float_range(0.10))) == 1  # type: ignore


def test_float_range_invalid_args():
    assert not list(float_range(0.40, 0.10, 0.01))  # type: ignore


def test_float_range_negative():
    assert len(list(float_range(0.40, 0.30, -0.1))) == 2  # type: ignore


@pytest.mark.repeat(10)
def test_get_random_words():
    word_list = random.choice(list(WORD_LISTS.values()))
    assert len(word_list)
    random_words = get_random_words(5, word_list=word_list)
    assert isinstance(random_words, str)
    random_words_list = random_words.split(",")
    assert all(word in word_list for word in random_words_list)


def test_get_random_words_max_length():
    word_list = ["cat", "bat", "rat", "donkey", "horse"]
    random_words = get_random_words(2, max_length=3, word_list=word_list)
    assert all(len(word) <= 3 for word in random_words)
