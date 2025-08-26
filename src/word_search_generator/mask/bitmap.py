from pathlib import Path
from typing import TYPE_CHECKING, cast

from PIL import Image, ImageChops

from ..utils import in_bounds
from .mask import Mask, MaskMethod, MaskNotGenerated, MethodLiteral

if TYPE_CHECKING:
    from collections.abc import Iterable


class ContrastError(Exception):
    pass


class Bitmap(Mask):
    """This class represents a subclass of the Mask object
    and generates a mask from a set of coordinate points."""

    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: MaskMethod | MethodLiteral = 1,
        static: bool = True,
    ) -> None:
        """Initialize a WordSearch puzzle bitmap mask object.

        Args:
            points (list[tuple[int, int]] | None, optional): Coordinate points
                used to build the mask. Defaults to None.
            method (int, optional): How Mask is applied to the puzzle
                (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.
            static (bool, optional): Should this mask be reapplied
                after changes to the parent puzzle size. Defaults to True.
        """
        super().__init__(points=points, method=method, static=static)

    def _draw(self) -> None:
        """Set each coordinate point from `object.points` as
        `ACTIVE` in `Object._mask`.

        Raises:
            MaskNotGenerated: Mask has not yet been generated.
        """
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `.generate()` method."
            )
        for x, y in self.points:
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self._mask[y][x] = self.ACTIVE


class ImageMask(Bitmap):
    """This class represents a subclass of the Bitmap object
    and generates a mask a mask from a raster image."""

    threshold = 200  # normalization contrast point

    def __init__(
        self,
        fp: str | Path,
        method: MaskMethod | MethodLiteral = 1,
        static: bool = False,
    ) -> None:
        """Generate a bitmap mask from a raster image.

        Note: Ideally, the raster image should be a single color (dark) on a solid
        or transparent background (think black pixels on white background).
        Multi-color images will work, but know that all colors will be converted
        to grayscale first.

        Args:
            fp (str | Path): A filepath (string) or `pathlib.Path` object
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
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        img = Image.open(self.fp, formats=("BMP", "JPEG", "PNG"))
        self.points = ImageMask.process_image(
            img, self.puzzle_size, ImageMask.threshold
        )
        if not self.points:
            raise ContrastError("The provided image lacked enough contrast.")
        self._draw()

    @staticmethod
    def process_image(
        image: Image.Image, size: int, threshold: int = 200
    ) -> list[tuple[int, int]]:
        """Convert to grayscale, threshold, resize, and return pixel coordinates."""

        grayscale_img: Image.Image = image.convert("L")

        bw_img: Image.Image = grayscale_img.point(
            lambda px: 255 if px > threshold else 0
        )

        diff: Image.Image = ImageChops.difference(
            bw_img, Image.new("L", bw_img.size, 255)
        )

        bbox: tuple[int, int, int, int] | None = diff.getbbox()
        if bbox is None:
            return []  # nothing but white

        cropped: Image.Image = bw_img.crop(bbox)

        cropped.thumbnail(size=(size, size), resample=Image.Resampling.NEAREST)

        assert cropped.mode == "L"
        pixels_iter = cast("Iterable[int]", cropped.getdata())
        pixels: list[int] = list(pixels_iter)

        w: int = cropped.size[0]
        return [(i % w, i // w) for i, px in enumerate(pixels) if px <= threshold]
