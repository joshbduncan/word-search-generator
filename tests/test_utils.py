from word_search_generator import utils
from word_search_generator.core.word import Word, Position
from word_search_generator.core.directions import Direction


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


def test_answer_key_list(ws, words):
    key_as_list = utils.get_answer_key_list(
        ws.hidden_words.union(ws.secret_words), ws.bounding_box
    )
    assert len(key_as_list) == len(ws.key)
    assert str(key_as_list[0]).lower().startswith(sorted(words.split(", "))[0].lower())


def test_float_range():
    assert len(list(utils.float_range(0.10))) == 1


def test_float_range_invalid_args():
    assert not list(utils.float_range(0.40, 0.10, 0.01))


def test_float_range_negative():
    assert len(list(utils.float_range(0.40, 0.30, -0.1))) == 2


def test_sort_words_if_needed_with_sorting():
    """Test sort_words_if_needed when sorting is enabled."""
    words = ['zebra', 'apple', 'cat', 'dog']
    result = utils.sort_words_if_needed(words, sort=True)
    assert result == ['apple', 'cat', 'dog', 'zebra']


def test_sort_words_if_needed_without_sorting():
    """Test sort_words_if_needed when sorting is disabled."""
    words = ['zebra', 'apple', 'cat', 'dog']
    result = utils.sort_words_if_needed(words, sort=False)
    assert result == ['zebra', 'apple', 'cat', 'dog']


def test_sort_words_if_needed_with_key_function():
    """Test sort_words_if_needed with custom key function."""
    words = [Word('zebra'), Word('apple'), Word('cat')]
    result = utils.sort_words_if_needed(words, sort=True, key_func=lambda w: w.text)
    expected_texts = ['APPLE', 'CAT', 'ZEBRA']
    assert [w.text for w in result] == expected_texts


def test_sort_words_if_needed_with_key_function_no_sorting():
    """Test sort_words_if_needed with custom key function but no sorting."""
    words = [Word('zebra'), Word('apple'), Word('cat')]
    result = utils.sort_words_if_needed(words, sort=False, key_func=lambda w: w.text)
    expected_texts = ['ZEBRA', 'APPLE', 'CAT']
    assert [w.text for w in result] == expected_texts


def test_get_word_list_list_with_sorting():
    """Test get_word_list_list with sorting enabled."""
    key = {
        'zebra': {'secret': False},
        'apple': {'secret': False},
        'cat': {'secret': True}  # secret word should be excluded
    }
    result = utils.get_word_list_list(key, sort_words=True)
    assert result == ['apple', 'zebra']


def test_get_word_list_list_without_sorting():
    """Test get_word_list_list with sorting disabled."""
    # Using ordered keys to test insertion order preservation
    key = {
        'zebra': {'secret': False},
        'apple': {'secret': False},
        'cat': {'secret': True}  # secret word should be excluded
    }
    result = utils.get_word_list_list(key, sort_words=False)
    # Note: dict key order in Python 3.7+ preserves insertion order
    expected = ['zebra', 'apple']
    assert result == expected


def test_get_answer_key_list_with_sorting():
    """Test get_answer_key_list with sorting enabled."""
    words = [Word('zebra'), Word('apple'), Word('cat')]
    # Set positions and directions for the words
    words[0].position = Position(0, 0)
    words[0].direction = Direction.E
    words[1].position = Position(1, 0)
    words[1].direction = Direction.E
    words[2].position = Position(2, 0)
    words[2].direction = Direction.E
    
    bbox = ((0, 0), (3, 3))
    result = utils.get_answer_key_list(words, bbox, sort_words=True)
    
    # Should be sorted alphabetically by word text
    assert 'APPLE' in result[0]
    assert 'CAT' in result[1] 
    assert 'ZEBRA' in result[2]


def test_get_answer_key_list_without_sorting():
    """Test get_answer_key_list with sorting disabled."""
    words = [Word('zebra'), Word('apple'), Word('cat')]
    # Set positions and directions for the words
    words[0].position = Position(0, 0)
    words[0].direction = Direction.E
    words[1].position = Position(1, 0)
    words[1].direction = Direction.E
    words[2].position = Position(2, 0)
    words[2].direction = Direction.E
    
    bbox = ((0, 0), (3, 3))
    result = utils.get_answer_key_list(words, bbox, sort_words=False)
    
    # Should maintain original order
    assert 'ZEBRA' in result[0]
    assert 'APPLE' in result[1]
    assert 'CAT' in result[2]
