import pytest

from word_search_generator.config import ACTIVE, INACTIVE
from word_search_generator.mask import CompoundMask, Mask, MaskNotGenerated


def test_mask_property_points_set_during_init():
    m = Mask([(1, 2), (3, 4)])
    assert len(m.points) == 2


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


def test_mask_property_puzzle_size_undefined():
    m = Mask()
    assert m.puzzle_size is None


def test_mask_property_puzzle_size_setter():
    size = 21
    m = Mask()
    m.puzzle_size = size
    assert m.puzzle_size == size


def test_mask_property_puzzle_size_setter_non_static():
    size = 21
    m = Mask(static=False)
    m.puzzle_size = size
    assert m.puzzle_size == size


def test_mask_property_puzzle_size_setter_invalid_type():
    m = Mask()
    with pytest.raises(TypeError):
        m.puzzle_size = "a"  # type: ignore  # noqa: F841


def test_mask_property_puzzle_size_setter_invalid_value():
    m = Mask()
    with pytest.raises(ValueError):
        m.puzzle_size = 7000  # type: ignore # noqa: F841


def test_mask_property_bounding_box():
    m = Mask([(1, 2), (3, 4)])
    assert m.bounding_box == ((1, 2), (3, 4))


def test_mask_property_bounding_box_unsorted():
    m = Mask([(3, 4), (1, 2)])
    assert m.bounding_box == ((1, 2), (3, 4))


def test_mask_property_bounding_box_no_points():
    m = Mask()
    assert m.bounding_box is None


def test_build_mask():
    size = 3
    char = "J"
    m = Mask.build_mask(size, char)
    assert m == [[char] * size] * size


def test_generate():
    size = 5
    m = Mask()
    m.generate(size)
    assert m.puzzle_size == size
    assert m.mask == [[INACTIVE] * size for _ in range(5)]


def test_show_not_generated():
    m = Mask()
    with pytest.raises(MaskNotGenerated):
        m.show()


def test_show(capsys):
    m = Mask([(1, 2), (3, 4)])
    m.generate(5)
    match = """# # # # #
# # # # #
# # # # #
# # # # #
# # # # #
"""
    m.show()
    capture = capsys.readouterr()
    assert capture.out == match


def test_show_active_only(capsys):
    size = 5
    m = Mask([(0, 0), (1, 1)])
    m.generate(size)
    for x, y in m.points:
        m.mask[y][x] = ACTIVE
    match = "*  \n  *\n"
    m.show(True)
    capture = capsys.readouterr()
    assert capture.out == match


def test_invert():
    m = Mask()
    m._mask = [
        [ACTIVE, INACTIVE, ACTIVE],
        [INACTIVE, ACTIVE, INACTIVE],
        [ACTIVE, INACTIVE, ACTIVE],
    ]
    m.invert()
    assert m.mask == [
        [INACTIVE, ACTIVE, INACTIVE],
        [ACTIVE, INACTIVE, ACTIVE],
        [INACTIVE, ACTIVE, INACTIVE],
    ]


def test_flip_horizontal():
    m = Mask()
    m._mask = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    m.flip_horizontal()
    assert m.mask == [[3, 2, 1], [6, 5, 4], [9, 8, 7]]


def test_flip_vertical():
    m = Mask()
    m._mask = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    m.flip_vertical()
    assert m.mask == [[7, 8, 9], [4, 5, 6], [1, 2, 3]]


def test_transpose():
    m = Mask()
    m._mask = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    m.transpose()
    assert m.mask == [[1, 4, 7], [2, 5, 8], [3, 6, 9]]


def test_ungenerated_mask():
    """Test MaskNotGenerated exception when mask hasn't been generated yet."""
    m = Mask()
    with pytest.raises(MaskNotGenerated):
        m._draw()


def test_empty_compound_mask():
    cm = CompoundMask()
    assert cm.masks == []


def test_compound_mask_masks_during_init():
    m1 = Mask()
    m2 = Mask()
    m3 = Mask()
    masks = [m1, m2, m3]
    cm = CompoundMask(masks)
    assert cm.masks == masks


def test_compound_mask_add_mask():
    m1 = Mask()
    m2 = Mask()
    m3 = Mask()
    masks = [m1, m2, m3]
    cm = CompoundMask([m1, m2])
    cm.add_mask(m3)
    assert cm.masks == masks


def test_compound_mask_bounding_box():
    size = 11
    cm = CompoundMask()
    cm.generate(size)
    assert cm.bounding_box == ((0, 0), (size - 1, size - 1))


def test_compound_mask_generate():
    size = 11
    cm = CompoundMask()
    cm.generate(size)
    assert cm.puzzle_size == size
    assert cm.mask == [[ACTIVE] * size] * size


def test_compound_mask_generate_submasks():
    size = 11
    m1 = Mask()
    cm = CompoundMask([m1])
    cm.generate(size)
    assert m1.puzzle_size == size
    assert m1.mask == [[INACTIVE] * size] * size


def test_compound_mask_apply_mask_error():
    m1 = Mask()
    cm = CompoundMask()
    with pytest.raises(MaskNotGenerated):
        cm._apply_mask(m1)


def test_compound_mask_apply_mask_method_1():
    size = 11
    m1 = Mask()
    m1.generate(size)
    m1.invert()
    cm = CompoundMask()
    cm.generate(size)
    cm._apply_mask(m1)
    assert m1.mask == cm.mask


def test_compound_mask_apply_mask_method_2():
    size = 11
    m1 = Mask(method=2)
    m1.generate(size)
    m1.invert()
    cm = CompoundMask()
    cm.generate(size)
    cm._apply_mask(m1)
    assert m1.mask == cm.mask


def test_compound_mask_apply_mask_method_3():
    size = 11
    m1 = Mask(method=3)
    m1.generate(size)
    m1.invert()
    cm = CompoundMask()
    cm.generate(size)
    cm._apply_mask(m1)
    assert cm.mask == [[INACTIVE] * size] * size
