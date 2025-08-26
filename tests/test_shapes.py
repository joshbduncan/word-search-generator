import io
from contextlib import redirect_stdout
from typing import TYPE_CHECKING

import pytest

from word_search_generator import WordSearch
from word_search_generator.core.game import EmptyPuzzleError
from word_search_generator.mask import shapes

if TYPE_CHECKING:
    from word_search_generator.mask import Mask


def test_not_generated_error():
    ws = WordSearch(size=21)
    with pytest.raises(EmptyPuzzleError):
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


def test_shape_mask_output(builtin_mask_shapes, builtin_mask_shapes_output):
    preview_size = 21
    for name, shape in builtin_mask_shapes.items():
        mask: Mask = shape()
        mask.generate(preview_size)

        with io.StringIO() as buf, redirect_stdout(buf):
            mask.show()
            output = buf.getvalue()

        assert builtin_mask_shapes_output[name] == output
