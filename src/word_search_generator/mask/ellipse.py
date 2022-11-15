import math
from typing import List, Optional, Tuple

from ..utils import distance, float_range
from . import Mask
from .bitmap import Bitmap


class Ellipse(Bitmap):
    """This subclass of `Bitmap` represents a Ellipse mask object."""

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        origin: Optional[Tuple[int, int]] = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        """Generate an ellipse mask.

        Args:
            width (Optional[int], optional): Ellipse width. Defaults to None.
            height (Optional[int], optional): Ellipse height. Defaults to None.
            origin (Optional[Tuple[int, int]], optional): Center origin point
            from which the polygon will be drawn. Defaults to puzzle center.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to True.
        """
        super().__init__(method=method, static=static)
        self.width = width
        self.height = height
        self.origin = origin

    def generate(
        self, puzzle_size: int, origin: Optional[Tuple[int, int]] = None
    ) -> None:
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(puzzle_size)
        # set origin point to center of puzzle if not specified
        self.origin = origin if origin else self.origin
        # if no size is specified, or size is too big, fill the puzzle
        if not self.width or self.width > puzzle_size:
            self.width = puzzle_size
        if not self.height or self.height > puzzle_size:
            self.height = puzzle_size
        self.points = Ellipse.calculate_ellipse_points(
            self.width,
            self.height,
            self.origin
            if self.origin
            else (self.puzzle_size // 2, self.puzzle_size // 2),
            puzzle_size,
        )
        self._draw()

    @staticmethod
    def calculate_ellipse_points(
        width: int,
        height: int,
        origin: Tuple[int, int],
        puzzle_size: int,
    ) -> List[Tuple[int, int]]:
        """Calculate all coordinates within an ellipse."""

        width_r = width // 2
        height_r = height // 2
        ratio = width_r / height_r

        # determine points to check for fitness inside of radius
        if (width_r * 2) % 2 == 0:
            max_pointsX = math.ceil(width_r - 0.5) * 2 + 1
        else:
            max_pointsX = math.ceil(width_r) * 2
        if (height_r * 2) % 2 == 0:
            max_pointsY = math.ceil(height_r - 0.5) * 2 + 1
        else:
            max_pointsY = math.ceil(height_r) * 2

        # calculate the origin offset
        if puzzle_size % 2 == 0 and width % 2 != 0:
            x_offset = origin[0] - 1
        else:
            x_offset = origin[0]
        if puzzle_size % 2 == 0 and height % 2 != 0:
            y_offset = origin[1] - 1
        else:
            y_offset = origin[1]

        # check all points and see if they fit inside of the ellipse
        points = []
        minY = -max_pointsY / 2 + 1
        maxY = max_pointsY / 2 - 1
        minX = -max_pointsX / 2 + 1
        maxX = max_pointsX / 2 - 1
        for y in float_range(minY, maxY + 1):
            for x in float_range(minX, maxX + 1):
                if Ellipse.within_radius(x, y, width_r, ratio):
                    points.append((int(x + x_offset), int(y + y_offset)))
        return points

    @staticmethod
    def within_radius(x: int, y: int, radius: float, ratio: float) -> bool:
        """Check if a coordinate is within a grid radius."""
        return distance(x, y, ratio) <= radius
