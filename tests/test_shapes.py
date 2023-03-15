import pytest

from word_search_generator import PuzzleNotGeneratedError, WordSearch
from word_search_generator.mask import shapes


def test_not_generated_error():
    p = WordSearch(size=21)
    with pytest.raises(PuzzleNotGeneratedError):
        p.apply_mask(shapes.Star5())


def test_min_size_club():
    p = WordSearch(size=8)
    p.random_words(10)
    with pytest.raises(ValueError):
        p.apply_mask(shapes.Club())


def test_min_size_fish():
    p = WordSearch(size=8)
    p.random_words(10)
    with pytest.raises(ValueError):
        p.apply_mask(shapes.Fish())


def test_min_size_flower():
    p = WordSearch(size=8)
    p.random_words(10)
    with pytest.raises(ValueError):
        p.apply_mask(shapes.Flower())


def test_min_size_spade():
    p = WordSearch(size=8)
    p.random_words(10)
    with pytest.raises(ValueError):
        p.apply_mask(shapes.Spade())
