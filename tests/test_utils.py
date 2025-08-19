from word_search_generator.utils import (
    float_range,
    get_answer_key_list,
    get_word_list_list,
    stringify,
)


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
