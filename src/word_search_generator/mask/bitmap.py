from pathlib import Path
from typing import List, Optional, Tuple, Union

from PIL import Image as PILImage
from PIL import ImageChops

from ..config import ACTIVE
from ..utils import in_bounds
from . import Mask, MaskNotGenerated


class ContrastError(Exception):
    ...


class Bitmap(Mask):
    """This class represents a subclass of the Mask object
    and generates a mask from a set of coordinate points."""

    def __init__(
        self,
        points: Optional[List[Tuple[int, int]]] = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        """Initialize a WordSearch puzzle bitmap mask object.

        Args:
            points (Optional[List[Tuple[int, int]]], optional): Coordinate points
                used to build the mask. Defaults to None.
            method (int, optional): How Mask is applied to the puzzle
                (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.
            static (bool, optional): Should this mask be reapplied
                after changes to the parent puzzle size. Defaults to True.
        """
        super().__init__(points=points, method=method, static=static)

    def _draw(self) -> None:
        """Set each coordinate point from `object.points` as
        `config.ACTIVE` in `Object._mask`.

        Raises:
            MaskNotGenerated: Mask has not yet been generated.
        """
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `.generate()` method."
            )
        for x, y in self.points:
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self._mask[y][x] = ACTIVE


class Image(Bitmap):
    """This class represents a subclass of the Bitmap object
    and generates a mask a mask from a raster image."""

    threshold = 200  # normalization contrast point

    def __init__(
        self, fp: Union[str, Path], method: int = 1, static: bool = False
    ) -> None:
        """Generate a bitmap mask from a raster image.

        Note: Ideally, the raster image should be a single color (dark) on a solid
        or transparent background (think black pixels on white background).
        Multi-color images will work, but know that all colors will be converted
        to grayscale first.

        Args:
            fp (Union[str, Path]): A filepath (string) or `pathlib.Path` object
                to the raster image the mask will be generated from.
            method (int, optional): How Mask is applied to the puzzle
                (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.
            static (bool, optional): Should this mask be reapplied
                after changes to the parent puzzle size. Defaults to True.
        """
        super().__init__(method=method, static=static)
        self.fp = fp

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size` from a raster image."""
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
    def process_image(image: PILImage, size: int, threshold: int = 200) -> PILImage:
        """Take a `PIL.Image` object, convert it to black-and-white, trim any
        excess pixels from the edges, resize it, and return all of the black
        pixels as a (x, y) coordinates."""
        image = image.convert("L").point(
            lambda px: 255 if px > Image.threshold else 0, mode="1"
        )
        diff = ImageChops.difference(image, PILImage.new("L", image.size, (255)))
        bbox = diff.getbbox()
        image = image.crop(bbox)
        image.thumbnail((size, size), resample=0)
        w, _ = image.size
        return [
            (0 if i == 0 else i % w, i // w)
            for i, px in enumerate(image.getdata())
            if px <= threshold
        ]
