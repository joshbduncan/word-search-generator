import inspect
import math
import sys

from ..config import ACTIVE, INACTIVE
from ..utils import build_puzzle
from . import (
    CompoundMask,
    ConvexPolygon,
    Ellipse,
    Polygon,
    Rectangle,
    calculate_ellipse_points,
    calculate_regular_convex_polygon_points,
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

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.width = puzzle_size
        self.height = puzzle_size
        self.points = calculate_ellipse_points(self.width, self.height, puzzle_size)
        self.draw()


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
        self.draw()


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


class EquilateralDiamond(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a EquilateralDiamond mask object."""

    def __init__(
        self, rotation: int = 0, method: int = 1, static: bool = False
    ) -> None:
        super().__init__(
            sides=4,
            rotation=rotation if rotation >= 0 else 360 + rotation,
            method=method,
            static=static,
        )


class EquilateralTriangle(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a EquilateralTriangle mask object."""

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
        self.draw()


class Hexagon(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a Hexagon mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(sides=6, method=method, static=static)


class Octagon(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a Octagon mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(sides=8, method=method, static=static)


class Pentagon(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a Pentagon mask object."""

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
        self, rotation: int = 0, method: int = 1, static: bool = False
    ) -> None:
        """Generate a regular 5-pointed star/pentagram mask.

        Note: An odd `puzzle_size` will generate a Isosceles Triangle and
        even `puzzle_size` will generate an Scalene Triangle.

        Args:
            rotation (int, optional): Rotation of shape within the puzzle.
            Defaults to 0.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        super().__init__(method=method, static=static)
        self.rotation = rotation if rotation >= 0 else 360 + rotation

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        points = calculate_regular_convex_polygon_points(puzzle_size, 5, self.rotation)
        self.points = [
            points[0],
            points[2],
            points[4],
            points[1],
            points[3],
            points[0],
        ]
        self.draw()


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
            position=(
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
        self.draw()


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
