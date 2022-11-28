import pytest

# from word_search_generator import WordSearch
from word_search_generator.mask import Mask, MaskNotGenerated

# Bitmap,
# CompoundMask,
# Ellipse,
# Image,
# Polygon,
# Rectangle,
# RegularPolygon,
# Star,


def test_mask_property_mask_empty():
    m = Mask()
    assert m.mask == []


def test_mask_property_method_undefined():
    m = Mask()
    assert m.method == 1


def test_mask_property_method_setter():
    m = Mask(method=2)
    assert m.method == 2


def test_mask_property_method_setter_invalid_type():
    with pytest.raises(TypeError):
        m = Mask(method="a")  # type: ignore  # noqa: F841


def test_mask_property_method_setter_invalid_value():
    with pytest.raises(ValueError):
        m = Mask(method=7)  # type: ignore # noqa: F841


def test_mask_property_static_undefined():
    m = Mask()
    assert m.static


def test_mask_property_static_setter():
    m = Mask(static=False)
    assert not m.static


def test_mask_property_static_setter_invalid():
    with pytest.raises(TypeError):
        m = Mask(static=7)  # type: ignore # noqa: F841


# def test_mask_property_puzzle_size():
#     pass


# def test_mask_property_bounding_box():
#     pass


# def test_generated_mask():
#     """Test MaskNotGenerated exception when mask hasn't been generated yet."""
#     m = Mask()
#     with pytest.raises(MaskNotGenerated):
#         m._draw()


def test_ungenerated_mask():
    """Test MaskNotGenerated exception when mask hasn't been generated yet."""
    m = Mask()
    with pytest.raises(MaskNotGenerated):
        m._draw()
