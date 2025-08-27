from pathlib import Path
from typing import TYPE_CHECKING, cast

from PIL import Image, ImageChops

from ..utils import in_bounds
from .mask import Mask, MaskMethod, MaskNotGenerated, MethodLiteral

if TYPE_CHECKING:
    from collections.abc import Iterable


class ContrastError(Exception):
    """Raised when an image lacks sufficient contrast for mask generation."""


class Bitmap(Mask):
    """This class represents a subclass of the Mask object
    and generates a mask from a set of coordinate points."""

    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = True,
    ) -> None:
        """Initialize a WordSearch puzzle bitmap mask object.

        Args:
            points: Coordinate points
                used to build the mask. Defaults to None.
            method: How Mask is applied to the puzzle
                (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.
            static: Should this mask be reapplied
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
    and generates a mask from a raster image."""

    threshold: int = 200  # normalization contrast point

    def __init__(
        self,
        fp: str | Path,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = False,
    ) -> None:
        """Generate a bitmap mask from a raster image.

        Args:
            fp: A filepath (string) or `pathlib.Path` object
                to the raster image the mask will be generated from.
            method: How Mask is applied to the puzzle. Defaults to INTERSECTION.
            static: Should this mask be reapplied after changes to the
                parent puzzle size. Defaults to False.

        Raises:
            TypeError: If fp is not a string or Path object.
            FileNotFoundError: If the image file doesn't exist.
        """
        if not isinstance(fp, str | Path):
            raise TypeError("`fp` must be a string or Path object")

        fp_path = Path(fp)
        if not fp_path.exists():
            raise FileNotFoundError(f"Image file not found: {fp}")
        if not fp_path.is_file():
            raise ValueError(f"Path is not a file: {fp}")

        super().__init__(method=method, static=static)
        self.fp = fp_path  # Store as Path object for consistency

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size` from a raster image.

        Raises:
            ContrastError: If the image lacks sufficient contrast.
            OSError: If the image file cannot be opened or read.
        """
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)

        try:
            with Image.open(self.fp, formats=("BMP", "JPEG", "PNG")) as img:
                self.points = ImageMask.process_image(
                    img, self.puzzle_size, ImageMask.threshold
                )
        except OSError as e:
            raise OSError(f"Failed to open image file {self.fp}: {e}") from e

        if not self.points:
            raise ContrastError(
                f"The provided image '{self.fp}' lacked sufficient contrast "
                f"(threshold={ImageMask.threshold})"
            )
        self._draw()

    @staticmethod
    def process_image(
        image: Image.Image, size: int, threshold: int = 200
    ) -> list[tuple[int, int]]:
        """Convert image to binary mask coordinates.

        Converts the image to grayscale, applies threshold to create a binary
        image, crops to content, resizes to fit the puzzle size, and returns
        coordinates of dark pixels.

        Args:
            image: PIL Image object to process.
            size: Target size for the mask (width and height).
            threshold: Pixel intensity threshold (0-255). Pixels below this
                value are considered "active" mask areas. Defaults to 200.

        Returns:
            List of (x, y) coordinate tuples for active mask pixels.
            Empty list if no contrast is found.

        Raises:
            TypeError: If image is not a PIL Image object.
            ValueError: If size <= 0 or threshold not in range 0-255.
        """
        # Input validation
        if not isinstance(image, Image.Image):
            raise TypeError("image must be a PIL Image object")
        if size <= 0:
            raise ValueError("size must be positive")
        if not 0 <= threshold <= 255:
            raise ValueError("threshold must be between 0 and 255")

        # Convert to grayscale
        grayscale_img: Image.Image = image.convert("L")

        # Apply threshold to create binary image
        bw_img: Image.Image = grayscale_img.point(
            lambda px: 255 if px > threshold else 0
        )

        # Find bounding box of non-white content
        diff: Image.Image = ImageChops.difference(
            bw_img, Image.new("L", bw_img.size, 255)
        )

        bbox: tuple[int, int, int, int] | None = diff.getbbox()
        if bbox is None:
            return []  # nothing but white

        # Crop to content and resize to target size
        cropped: Image.Image = bw_img.crop(bbox)
        cropped.thumbnail(size=(size, size), resample=Image.Resampling.NEAREST)

        # Extract pixel data and convert to coordinates
        assert cropped.mode == "L"
        pixels_iter = cast("Iterable[int]", cropped.getdata())
        pixels: list[int] = list(pixels_iter)

        w: int = cropped.size[0]
        return [(i % w, i // w) for i, px in enumerate(pixels) if px <= threshold]
