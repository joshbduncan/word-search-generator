import math

from ..utils import distance, float_range
from .bitmap import Bitmap
from .mask import MaskMethod, MethodLiteral


class Ellipse(Bitmap):
    """Generates ellipse-shaped masks for word search puzzles.

    Creates elliptical mask shapes that can be used to constrain word
    placement within an ellipse boundary. Supports custom dimensions
    and positioning within the puzzle grid.
    """

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        center: tuple[int, int] | None = None,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = True,
    ) -> None:
        """Generate an ellipse mask.

        Args:
            width: Ellipse width.
                Defaults to `puzzle_size` provided to the `.generate()` method.
            height: Ellipse height.
                Defaults to `puzzle_size` provided to the `.generate()` method.
            center: Center origin point from which the ellipse will be calculated.
                Defaults to puzzle center. Coordinates can be negative for shapes
                that extend outside grid bounds.
            method: How Mask is applied to the puzzle. Defaults to INTERSECTION.
            static: Should this mask be reapplied after changes
                to the parent puzzle size. Defaults to True.

        Raises:
            ValueError: If width or height are <= 0, or if center is invalid.
            TypeError: If center is not a tuple of two numbers.
        """
        if width is not None and width <= 0:
            raise ValueError("width must be positive")
        if height is not None and height <= 0:
            raise ValueError("height must be positive")

        if center is not None:
            if not isinstance(center, tuple) or len(center) != 2:
                raise TypeError("center must be a tuple of two coordinates")
            if not all(isinstance(coord, int | float) for coord in center):
                raise TypeError("center coordinates must be numbers")
            if not all(math.isfinite(coord) for coord in center):
                raise ValueError("center coordinates must be finite")
            # Note: Negative coordinates are allowed for mathematical flexibility

        super().__init__(method=method, static=static)
        self.width = width
        self.height = height
        self.center = center

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self.points = Ellipse.calculate_ellipse_points(
            self.width if self.width else self.puzzle_size,
            self.height if self.height else self.puzzle_size,
            (
                self.center
                if self.center
                else (self.puzzle_size // 2, self.puzzle_size // 2)
            ),
            puzzle_size,
        )
        self._draw()

    @staticmethod
    def calculate_ellipse_points(
        width: int,
        height: int,
        origin: tuple[int, int],
        puzzle_size: int,
    ) -> list[tuple[int, int]]:
        """Calculate all coordinates within an ellipse.

        Args:
            width: Width of the ellipse.
            height: Height of the ellipse.
            origin: Center point of the ellipse.
            puzzle_size: Size of the puzzle grid.

        Returns:
            List of coordinate tuples within the ellipse bounds.

        Raises:
            ValueError: If width, height, or puzzle_size are <= 0,
                or if origin is invalid.
        """
        # Input validation
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        if puzzle_size <= 0:
            raise ValueError("puzzle_size must be positive")
        if len(origin) != 2:
            raise ValueError("origin must be a tuple of two coordinates")
        if not all(isinstance(coord, int | float) for coord in origin):
            raise ValueError("origin coordinates must be numbers")
        if not all(math.isfinite(coord) for coord in origin):
            raise ValueError("origin coordinates must be finite")
        # Note: Negative coordinates are allowed for mathematical flexibility

        # Calculate ellipse parameters
        width_radius: float = width / 2
        height_radius: float = height / 2
        ratio: float = width_radius / height_radius

        # Determine search area bounds for ellipse points
        max_points_x: int = (
            math.ceil(width_radius - 0.5) * 2 + 1
            if (width_radius * 2) % 2 == 0
            else math.ceil(width_radius) * 2
        )

        max_points_y: int = (
            math.ceil(height_radius - 0.5) * 2 + 1
            if (height_radius * 2) % 2 == 0
            else math.ceil(height_radius) * 2
        )

        # Calculate the origin offset for proper centering
        x_offset: int = (
            origin[0] - 1 if puzzle_size % 2 == 0 and width % 2 != 0 else origin[0]
        )
        y_offset: int = (
            origin[1] - 1 if puzzle_size % 2 == 0 and height % 2 != 0 else origin[1]
        )

        # Define search boundaries
        min_y: float = -max_points_y / 2 + 1
        max_y: float = max_points_y / 2 - 1
        min_x: float = -max_points_x / 2 + 1
        max_x: float = max_points_x / 2 - 1

        # Generate all points within the ellipse
        points: list[tuple[int, int]] = []
        for y in float_range(min_y, max_y + 1):
            for x in float_range(min_x, max_x + 1):
                if Ellipse.within_radius(x, y, width_radius, ratio):
                    points.append((int(x + x_offset), int(y + y_offset)))

        return points

    @staticmethod
    def within_radius(
        x: int | float, y: int | float, radius: float, ratio: float
    ) -> bool:
        """Check if a coordinate is within the ellipse radius.

        Args:
            x: X coordinate relative to ellipse center.
            y: Y coordinate relative to ellipse center.
            radius: Semi-major axis radius of the ellipse.
            ratio: Ratio of width radius to height radius.

        Returns:
            True if the point is within the ellipse bounds.
        """
        return distance(x, y, ratio) <= radius
