from word_search_generator.word import Direction, Position, Word


def test_empty_start_row():
    w = Word("test")
    assert not w.start_row


def test_empty_start_column():
    w = Word("test")
    assert not w.start_column


def test_empty_position():
    w = Word("test")
    assert w.position == Position(None, None)


def test_position_xy():
    w = Word("test")
    w.start_row = 1
    w.start_column = 1
    assert w.position_xy == "(2, 2)"


def test_empty_position_xy():
    w = Word("test")
    assert not w.position_xy


def test_position_setter():
    p = Position(1, 2)
    w = Word("test")
    w.position = p
    assert w.start_row == p.row and w.start_column == p.column


def test_inequality():
    w = Word("test")
    assert w != "test"


def test_repr():
    w = Word("test")
    w.direction = Direction.S
    w.position = Position(1, 2)
    assert eval(repr(w)) == w


def test_str():
    w = Word("test")
    assert str(w) == "test".upper()


def test_empty_key_string():
    w = Word("test")
    assert w.key_string(((0, 0), (10, 10))) is None


def test_offset_empty_position_xy():
    w = Word("test")
    assert w.offset_position_xy(((0, 0), (10, 10))) is None
