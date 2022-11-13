import inspect
import math
import sys

from ..config import ACTIVE, INACTIVE
from ..utils import build_puzzle
from . import (
    CompoundMask,
    Ellipse,
    Polygon,
    Rectangle,
    RegularPolygon,
    calculate_ellipse_points,
    calculate_regular_regular_polygon_points,
)


def get_shape_objects():
    """Return all built-in shape objects from this file"""
    return [
        name
        for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
        if obj.__module__ is __name__
    ]


class Circle(Ellipse):
    """This subclass of `Ellipse` represents a Circle mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(method=method, static=static)

    def generate(
        self,
        puzzle_size: int,
        origin=None,
    ) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.width = puzzle_size
        self.height = puzzle_size
        self.origin = (puzzle_size // 2, puzzle_size // 2)
        self.points = calculate_ellipse_points(
            self.width,
            self.height,
            self.origin,
            puzzle_size,
        )
        self._draw()


class Diamond(Polygon):
    """This subclass of `Polygon` represents a Diamond mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        """Generate a diamond mask that fills the entire `puzzle_size`.

        Args:
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        super().__init__(method=method, static=static)

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.width = puzzle_size - 2 if puzzle_size % 2 == 0 else puzzle_size - 1
        self.height = puzzle_size - 1
        self.points = [
            (self.width // 2, 0),
            (0, self.height // 2),
            (self.width // 2, self.height),
            (self.width, self.height // 2),
        ]
        self._draw()


class Donut(CompoundMask):
    """This subclass of `CompoundMask` represents a Donut mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(method=method, static=static)

    def generate(self, puzzle_size: int) -> None:
        """Generate a mask at `puzzle_size`."""
        self.mask = build_puzzle(puzzle_size, ACTIVE)
        self.puzzle_size = puzzle_size
        outside_d = (
            self.puzzle_size - 1 if self.puzzle_size % 2 == 0 else self.puzzle_size
        )
        hole_d = int(math.pow(self.puzzle_size - 2, 2) // (3 * (self.puzzle_size - 1)))
        if hole_d % 2 == 0:
            hole_d += 1
        self.masks = [
            Ellipse(outside_d, outside_d),
            Ellipse(hole_d, hole_d, method=3),
        ]
        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_masks(mask)


class EquilateralDiamond(RegularPolygon):
    """This subclass of `RegularPolygon` represents a EquilateralDiamond mask object."""

    def __init__(
        self, rotation: int = 0, method: int = 1, static: bool = False
    ) -> None:
        super().__init__(
            sides=4,
            rotation=rotation if rotation >= 0 else 360 + rotation,
            method=method,
            static=static,
        )


class EquilateralTriangle(RegularPolygon):
    """This subclass of `RegularPolygon` represents a
    EquilateralTriangle mask object."""

    def __init__(
        self, rotation: int = 0, method: int = 1, static: bool = False
    ) -> None:
        super().__init__(
            sides=3,
            rotation=rotation if rotation >= 0 else 360 + rotation,
            method=method,
            static=static,
        )


class Heart(Polygon):
    """This subclass of `Polygon` represents a Heart mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        """Generate a 'heart-like' mask.
        Args:
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        super().__init__(method=method, static=static)

    def generate(self, puzzle_size: int) -> None:
        # FIXME: min calc for heart if 11 otherwise calculations break
        if puzzle_size < 8:
            puzzle_size = 8
        self.puzzle_size = puzzle_size - 1 if puzzle_size % 2 == 0 else puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.points = [
            (self.puzzle_size // 2, self.puzzle_size // 4),
            (self.puzzle_size // 8 * 3, 0),
            (self.puzzle_size // 8 * 2, 0),
            (0, self.puzzle_size // 4),
            (0, self.puzzle_size // 2),
            (self.puzzle_size // 2, self.puzzle_size - 1),
            (self.puzzle_size - 1, self.puzzle_size // 2),
            (self.puzzle_size - 1, self.puzzle_size // 4),
            ((self.puzzle_size - 1) - self.puzzle_size // 8 * 2, 0),
            ((self.puzzle_size - 1) - self.puzzle_size // 8 * 3, 0),
            (self.puzzle_size // 2, self.puzzle_size // 4),
        ]
        self._draw()


class Hexagon(RegularPolygon):
    """This subclass of `RegularPolygon` represents a Hexagon mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(sides=6, method=method, static=static)


class Octagon(RegularPolygon):
    """This subclass of `RegularPolygon` represents a Octagon mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(sides=8, method=method, static=static)


class Pentagon(RegularPolygon):
    """This subclass of `RegularPolygon` represents a Pentagon mask object."""

    def __init__(self, rotation: int = 0, method: int = 1) -> None:
        super().__init__(
            sides=5,
            rotation=rotation if rotation >= 0 else 360 + rotation,
            method=method,
        )


class SixPointedStar(CompoundMask):
    """This subclass of `CompoundMask` represents a SizPointedStar mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(method=method, static=static)
        self.masks = [
            (EquilateralTriangle()),
            (EquilateralTriangle(rotation=180, method=2)),
        ]


class Star(Polygon):
    """This subclass of `Polygon` represents a Star mask object."""

    def __init__(
        self, sides: int = 5, rotation: int = 0, method: int = 1, static: bool = False
    ) -> None:
        """Generate a regular star mask with `sides` points.

        Note: An odd `puzzle_size` will generate a Isosceles Triangle and
        even `puzzle_size` will generate an Scalene Triangle.

        Args:
            sides (int, optional): Sides or vertices of star. Defaults to 5.
            rotation (int, optional): Rotation of shape within the puzzle.
            Defaults to 0.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        # TODO: add size argument
        # TODO: add sized argument
        super().__init__(method=method, static=static)
        self.rotation = rotation if rotation >= 0 else 360 + rotation

    def generate(self, puzzle_size: int) -> None:
        def distance(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

        def mid_point(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return ((x1 - x2) * 0.5, (y1 - y2) * 0.5)

        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)

        center = (puzzle_size // 2, puzzle_size // 2)
        points = 5

        outer_points = calculate_regular_regular_polygon_points(
            puzzle_size, center, points, self.rotation
        )

        internal_angle = (points - 2) * math.pi / points
        mid_point_coords = mid_point(outer_points[0], outer_points[1])
        opp = distance(outer_points[0], mid_point_coords)
        theta = internal_angle * 0.5
        distance_in = opp / math.tan(theta)

        inner_radius = distance(center, mid_point_coords) - distance_in
        inner_points = calculate_regular_regular_polygon_points(
            inner_radius, center, points, self.rotation + 180
        )

        self.points = [
            outer_points[0],
            inner_points[3],
            outer_points[1],
            inner_points[4],
            outer_points[2],
            inner_points[0],
            outer_points[3],
            inner_points[1],
            outer_points[4],
            inner_points[2],
        ]
        self._draw()


class Tree(CompoundMask):
    """This subclass of `CompoundMask` represents a Tree mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(method=method, static=static)

    def generate(self, puzzle_size: int) -> None:
        """Generate a mask at `puzzle_size`."""
        self.mask = build_puzzle(puzzle_size, ACTIVE)
        self.puzzle_size = puzzle_size
        tree_top = EquilateralTriangle()
        tree_top.generate(self.puzzle_size)
        tree_top_width = tree_top.points[2][0] - tree_top.points[1][0] + 1
        tree_trunk_width = (
            tree_top_width // 4 + 1
            if tree_top_width // 4 % 2 == 0
            else tree_top_width // 4
        )
        tree_trunk_height = self.puzzle_size - tree_top.points[1][1]
        tree_trunk_position_x = (
            self.puzzle_size // 2 - tree_trunk_width // 2 - 1
            if self.puzzle_size % 2 == 0
            else self.puzzle_size // 2 - tree_trunk_width // 2
        )
        tree_trunk_position_y = tree_top.points[1][1]
        tree_trunk = Rectangle(
            width=tree_trunk_width,
            height=tree_trunk_height,
            origin=(
                tree_trunk_position_x,
                tree_trunk_position_y,
            ),
            method=2,
        )
        tree_trunk.generate(self.puzzle_size)
        self.masks = [tree_top, tree_trunk]
        for mask in self.masks:
            self._apply_masks(mask)


class Triangle(Polygon):
    """This subclass of `Polygon` represents a Triangle mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        """Generate a triangle mask that fills the entire `puzzle_size`.

        Note: An odd `puzzle_size` will generate a Isosceles Triangle and
        even `puzzle_size` will generate an Scalene Triangle.

        Args:
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        super().__init__(method=method, static=static)

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.width = puzzle_size - 2 if puzzle_size % 2 == 0 else puzzle_size - 1
        self.height = puzzle_size - 1
        self.points = [
            (self.width // 2, 0),
            (0, self.height),
            (self.width, self.height),
        ]
        self._draw()


# ********************************************************* #
# ******************** BUILT-IN SHAPES ******************** #
# ********************************************************* #

BUILTIN_SHAPES = {
    "circle": Circle(),
    "diamond": EquilateralDiamond(),
    "triangle": EquilateralTriangle(),
    "heart": Heart(),
    "hexagon": Hexagon(),
    "octagon": Octagon(),
    "pentagon": Pentagon(),
    "star": Star(),
}

BUILTIN_SHAPES = get_shape_objects()
