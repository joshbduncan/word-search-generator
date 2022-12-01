from pathlib import Path

import pytest
from PIL import Image as PILImage

from word_search_generator.config import ACTIVE
from word_search_generator.mask import Mask, MaskNotGenerated
from word_search_generator.mask.bitmap import Bitmap, ContrastError, Image


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
