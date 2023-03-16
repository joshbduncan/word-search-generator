from pathlib import Path

import pytest
from PIL import Image as PILImage

from word_search_generator import WordSearch
from word_search_generator.config import ACTIVE, INACTIVE
from word_search_generator.mask import CompoundMask, Mask, MaskNotGenerated
from word_search_generator.mask.bitmap import Bitmap, ContrastError, Image
from word_search_generator.mask.ellipse import Ellipse
from word_search_generator.mask.polygon import Polygon, RegularPolygon, Star
from word_search_generator.mask.shapes import Circle, Heart
from word_search_generator.utils import get_random_words


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
    assert m.puzzle_size == 0


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


# ************************************************ #
# ******************** BITMAP ******************** #
# ************************************************ #


def test_bitmap_mask_init():
    bm = Bitmap(method=2, static=False)
    assert isinstance(bm, Mask)
    assert bm.method == 2
    assert bm.static is False


def test_bitmap_mask_draw():
    size = 5
    bm = Bitmap([(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)])
    bm.generate(size)
    test_mask = [
        ["*", "#", "#", "#", "#"],
        ["#", "*", "#", "#", "#"],
        ["#", "#", "*", "#", "#"],
        ["#", "#", "#", "*", "#"],
        ["#", "#", "#", "#", "*"],
    ]
    assert bm.mask == test_mask


def test_bitmap_mask_draw_exception():
    bm = Bitmap()
    with pytest.raises(MaskNotGenerated):
        bm._draw()


def test_image_mask_init(tmp_path):
    name = "test_image.jpg"
    path = Path.joinpath(tmp_path, name)
    im = Image(path, method=2, static=False)
    assert isinstance(im, Mask)
    assert im.fp == path
    assert im.method == 2
    assert im.static is False


def test_image_mask_solid_black(tmp_path):
    name = "test_image_black.jpg"
    test_img = PILImage.new("L", (100, 100), (0))
    img_path = Path.joinpath(tmp_path, name)
    test_img.save(img_path, "JPEG")
    size = 11
    im = Image(img_path)
    im.generate(size)
    assert im.mask == [[ACTIVE] * size] * size


def test_image_mask_contrast_exception(tmp_path):
    name = "test_image_white.png"
    test_img = PILImage.new("L", (100, 100), (255))
    img_path = Path.joinpath(tmp_path, name)
    test_img.save(img_path, "PNG")
    size = 11
    im = Image(img_path)
    with pytest.raises(ContrastError):
        im.generate(size)


# ************************************************* #
# ******************** ELLIPSE ******************** #
# ************************************************* #


def test_calculate_ellipse_points_method_1():
    """Even `puzzle_size`, odd `width` and `height`."""
    puzzle_size = 6
    points = Ellipse.calculate_ellipse_points(
        width=5,
        height=3,
        origin=(puzzle_size // 2, puzzle_size // 2),
        puzzle_size=puzzle_size,
    )
    assert len(points) % 2 == 1


def test_calculate_ellipse_points_method_2():
    """Odd `puzzle_size`, even `width` and `height`."""
    puzzle_size = 7
    points = Ellipse.calculate_ellipse_points(
        width=6,
        height=4,
        origin=(puzzle_size // 2, puzzle_size // 2),
        puzzle_size=puzzle_size,
    )
    assert len(points) % 2 == 0


def test_within_radius_true():
    width = 10
    height = 6
    width_r = width / 2
    height_r = height / 2
    ratio = width_r / height_r
    assert Ellipse.within_radius(1, 2, width_r, ratio)


def test_within_radius_false():
    width = 4
    height = 2
    width_r = width / 2
    height_r = height / 2
    ratio = width_r / height_r
    assert not Ellipse.within_radius(7, 11, width_r, ratio)


# ************************************************* #
# ******************** POLYGON ******************** #
# ************************************************* #


def test_polygon_too_few_points():
    with pytest.raises(ValueError):
        pm = Polygon(((0, 0), (1, 1)))  # type: ignore # noqa: F841


def test_connect_points_no_generated():
    pm = Polygon()
    with pytest.raises(MaskNotGenerated):
        pm._connect_points((0, 0), (1, 1))


def test_fill_shape_not_generated():
    pm = Polygon()
    with pytest.raises(MaskNotGenerated):
        pm._fill_shape("J")


def test_generate_method_no_size():
    m = Mask()
    with pytest.raises(TypeError):
        m.generate()  # type: ignore


def test_regular_polygon_too_few_vertices():
    with pytest.raises(ValueError):
        pm = RegularPolygon(2)  # noqa: F841


def test_star_polygon_too_few_vertices():
    with pytest.raises(ValueError):
        pm = Star(2)  # noqa: F841


# ************************************************ #
# ******************** SHAPES ******************** #
# ************************************************ #


def test_heart_puzzle_too_small():
    m = Heart()
    with pytest.raises(ValueError):
        m.generate(7)


# **************************************************** #
# ******************** WORDSEARCH ******************** #
# **************************************************** #


def test_masked_property_true():
    p = WordSearch("pig horse cow")
    p.apply_mask(Star(5))
    assert p.masked


def test_masked_property_false():
    p = WordSearch("pig horse cow")
    assert not p.masked


def test_add_mask_error():
    p = WordSearch("pig horse cow")
    with pytest.raises(TypeError):
        p.apply_mask("J")  # type: ignore


def test_apply_mask_method_1():
    p = WordSearch(",".join(get_random_words(10)), size=10)
    p.apply_mask(Circle())
    assert p.puzzle[0][0] == ""
    assert p.puzzle[0][p.size - 1] == ""
    assert p.puzzle[p.size - 1][0] == ""
    assert p.puzzle[p.size - 1][p.size - 1] == ""


def test_apply_mask_method_2():
    size = 10
    p = WordSearch(",".join(get_random_words(10)), size=size)
    m1 = Mask()
    m1.generate(size)
    p.apply_mask(m1)
    m2 = Mask(method=2)
    m2.generate(size)
    m2.invert()
    p.apply_mask(m2)
    assert p.puzzle[0][0] != ""
    assert p.puzzle[0][p.size - 1] != ""
    assert p.puzzle[p.size - 1][0] != ""
    assert p.puzzle[p.size - 1][p.size - 1] != ""


def test_apply_mask_method_3():
    size = 10
    p = WordSearch(",".join(get_random_words(10)), size=size)
    m1 = Mask()
    m1.generate(size)
    m1.invert()
    p.apply_mask(m1)
    p.apply_mask(Ellipse(method=3))
    assert p.puzzle[size // 2][size // 2] == ""


def test_apply_masks():
    size = 21
    p = WordSearch("pig horse cow", size=size)
    p.apply_masks([Circle(), Ellipse(2, 2, method=3)])
    assert len(p.masks) == 2
    assert p.puzzle[size // 2][size // 2] == ""


def test_show_mask(capsys):
    size = 5
    p = WordSearch("pig horse cow", size=size)
    p.apply_mask(Circle())
    match = """# * * * #
* * * * *
* * * * *
* * * * *
# * * * #
"""
    p.show_mask()
    capture = capsys.readouterr()
    assert capture.out == match


def test_show_mask_empty(capsys):
    size = 5
    p = WordSearch("pig horse cow", size=size)
    p.show_mask()
    capture = capsys.readouterr()
    assert capture.out == "Empty mask.\n"


def test_puzzle_invert_mask():
    size = 21
    p = WordSearch("pig horse cow", size=size)
    p.apply_mask(Circle())
    p.invert_mask()
    assert p.puzzle[0][0] != ""
    assert p.puzzle[0][p.size - 1] != ""
    assert p.puzzle[p.size - 1][0] != ""
    assert p.puzzle[p.size - 1][p.size - 1] != ""


def test_puzzle_flip_mask_horizontal():
    size = 6
    p = WordSearch("pig horse cow", size=size)
    m = Polygon([(0, 0), (0, size - 1), (2, size - 1), (2, 0)])
    p.apply_mask(m)
    p.flip_mask_horizontal()
    assert p.mask == [r[::-1] for r in m.mask]


def test_puzzle_flip_mask_vertical():
    size = 6
    p = WordSearch("pig horse cow", size=size)
    m = Polygon([(0, 0), (size - 1, 0), (size - 1, 2), (0, 2)])
    p.apply_mask(m)
    p.flip_mask_vertical()
    assert p.mask == m.mask[::-1]


def test_puzzle_transpose_mask():
    size = 6
    p = WordSearch("pig horse cow", size=size)
    m1 = Polygon([(0, 0), (0, size - 1), (2, size - 1), (2, 0)])
    m2 = Polygon([(0, 0), (size - 1, 0), (size - 1, 2), (0, 2)])
    m2.generate(size)
    p.apply_mask(m1)
    p.transpose_mask()
    assert p.mask == m2.mask


def test_remove_masks():
    p = WordSearch("pig horse cow")
    p.apply_masks([Circle(), Ellipse(2, 2, method=3)])
    p.remove_masks()
    assert p.masks == []
    assert not p.masked


def test_remove_static_masks():
    p = WordSearch("pig horse cow")
    p.apply_masks([Star(), Ellipse(2, 2, method=3)])
    assert len(p.masks) == 2
    p.remove_static_masks()
    assert len(p.masks) == 1


def test_reapply_masks_static():
    p = WordSearch("pig horse cow")
    p.apply_mask(Circle())
    assert p.puzzle[0][0] == ""
    assert p.puzzle[0][p.size - 1] == ""
    assert p.puzzle[p.size - 1][0] == ""
    assert p.puzzle[p.size - 1][p.size - 1] == ""
    p.size = 30
    p._reapply_masks()
    assert p.puzzle[0][0] != ""
    assert p.puzzle[0][p.size - 1] != ""
    assert p.puzzle[p.size - 1][0] != ""
    assert p.puzzle[p.size - 1][p.size - 1] != ""


def test_reapply_masks_dynamic_scale_up():
    p = WordSearch("pig horse cow", size=11)
    p.apply_mask(Star())
    ct = sum([1 for x in p.puzzle if x != ""])  # type: ignore
    p.size = 21
    assert ct != sum([1 for x in p.puzzle if x != ""])  # type: ignore


def test_reapply_masks_dynamic_scale_down():
    p = WordSearch("pig horse cow", size=21)
    p.apply_mask(Star())
    ct = sum([1 for x in p.puzzle if x != ""])  # type: ignore
    p.size = 11
    assert ct != sum([1 for x in p.puzzle if x != ""])  # type: ignore
