import io
from contextlib import redirect_stdout

import pytest

from word_search_generator.game.word_search import PuzzleNotGeneratedError, WordSearch
from word_search_generator.mask import shapes


def test_not_generated_error():
    ws = WordSearch(size=21)
    with pytest.raises(PuzzleNotGeneratedError):
        ws.apply_mask(shapes.Star5())


def test_min_size_club():
    ws = WordSearch(size=8)
    ws.random_words(10)
    with pytest.raises(ValueError):
        ws.apply_mask(shapes.Club())


def test_min_size_fish():
    ws = WordSearch(size=8)
    ws.random_words(10)
    with pytest.raises(ValueError):
        ws.apply_mask(shapes.Fish())


def test_min_size_flower():
    ws = WordSearch(size=8)
    ws.random_words(10)
    with pytest.raises(ValueError):
        ws.apply_mask(shapes.Flower())


def test_min_size_spade():
    ws = WordSearch(size=8)
    ws.random_words(10)
    with pytest.raises(ValueError):
        ws.apply_mask(shapes.Spade())


def test_shape_mask_output(builtin_mask_shapes_output):
    preview_size = 21
    for shape in shapes.BUILTIN_MASK_SHAPES:
        mask = eval(f"shapes.{shape}")()
        mask.generate(preview_size)

        with io.StringIO() as buf, redirect_stdout(buf):
            mask.show()
            output = buf.getvalue()

        assert builtin_mask_shapes_output[shape] == output
