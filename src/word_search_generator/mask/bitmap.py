from collections import Counter
from pathlib import Path
from typing import Any, List, Tuple, Union

from PIL import Image as PILImage
from PIL import ImageChops

from ..config import ACTIVE
from ..utils import in_bounds
from . import Mask, MaskNotGenerated


class ContrastError(Exception):
    ...


class Bitmap(Mask):
    """This subclass of `Mask` represents Bitmap mask object."""

    def __init__(
        self, points: List[Any] = [], method: int = 1, static: bool = True
    ) -> None:
        super().__init__(points=points, method=method, static=static)

    def _draw(self) -> None:
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `Polygon.generate()` method."
            )
        for x, y in self.points:
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self.mask[y][x] = ACTIVE


class Image(Bitmap):
    """This subclass of `Bitmap` represents a Image mask object."""

    threshold = 200

    def __init__(
        self, fp: Union[str, Path], method: int = 1, static: bool = False
    ) -> None:
        """Generate a mask from a raster image.

        Args:
            fp (Union[str, Path]): A filename (string), pathlib.Path object.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        super().__init__(method=method, static=static)
        self.fp = fp

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(self.puzzle_size)
        self.points = Image.process_image(
            PILImage.open(self.fp, formats=("BMP", "JPEG", "PNG")),
            self.puzzle_size,
            Image.threshold,
        )
        if not self.points:
            raise ContrastError("The provided image lacked enough contrast.")
        self._draw()

    @staticmethod
    def normalize_rgb_values(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Clean-up any slight color differences in PIL color sampling."""
        return (
            0 if color[0] <= 3 else 255,
            0 if color[1] <= 3 else 255,
            0 if color[2] <= 3 else 255,
        )

    @staticmethod
    def trim_excess(image: PILImage) -> PILImage:
        """Trim excess background pixels from around `image`."""
        w, h = image.size
        # get RGB value for each corner of image
        corners = [
            Image.normalize_rgb_values(image.getpixel((0, 0))),
            Image.normalize_rgb_values(image.getpixel((w - 1, 0))),
            Image.normalize_rgb_values(image.getpixel((0, h - 1))),
            Image.normalize_rgb_values(image.getpixel((w - 1, h - 1))),
        ]
        # count how many times each value is present
        color_count = Counter([pixel for pixel in corners]).most_common()
        # if multiple corners have the same pixel count don't trim
        if len(color_count) > 1 and color_count[0][1] == color_count[1][1]:
            return image
        else:  # set the comparison pixel to the most common value
            bg_pixel = color_count[0][0]
        # compare the original image to the excess pixels and crop
        comp = PILImage.new("RGB", image.size, bg_pixel)
        diff = ImageChops.difference(image, comp)
        bbox = diff.getbbox()
        return image.crop(bbox)

    @staticmethod
    def process_image(image: PILImage, size: int, threshold: int = 200) -> PILImage:
        """Process `image` for bitmap mask capture."""
        # composite the image on a white background just in case it has transparency
        image = image.convert("RGBA")
        bg = PILImage.new("RGBA", image.size, (255, 255, 255))
        image = PILImage.alpha_composite(bg, image)
        # convert composite image to RGB since we don't need transparency
        image = image.convert("RGB")
        # trim excess background pixels
        image = Image.trim_excess(image)
        # resize the image so the bitmap matches the puzzle size
        image.thumbnail((size, size), resample=0)
        # convert image to black and white
        image = image.convert("L").point(
            lambda px: 255 if px > threshold else 0, mode="1"
        )
        # return all black pixels from the mask
        w, _ = image.size
        return [
            (0 if i == 0 else i % w, i // w)
            for i, px in enumerate(image.getdata())
            if px <= threshold
        ]
