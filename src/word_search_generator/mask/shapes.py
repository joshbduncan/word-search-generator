import inspect
import math
import sys

from . import Bitmap, CompoundMask, Mask
from .ellipse import Ellipse
from .mask import MaskMethod
from .polygon import Polygon, Rectangle, RegularPolygon, Star


def get_shape_objects() -> dict[str, type[Mask]]:
    """Return all built-in preset shape classes from this file, keyed by lowercase name.

    Excludes utility base classes that require parameters for instantiation.
    Only includes concrete shape classes that can be instantiated without arguments.
    """
    # Utility classes that shouldn't be directly instantiated by users
    utility_classes = {
        "Bitmap",
        "CompoundMask",
        "Mask",
        "Ellipse",
        "Polygon",
        "Rectangle",
        "RegularPolygon",
        "Star",
    }

    # Concrete user-facing shapes that should always be included
    # even if they inherit from utility classes
    concrete_shapes = {
        "Square",
        "Oval",
    }

    return {
        name.lower(): obj
        for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
        if (
            obj.__module__ is __name__
            and issubclass(obj, Mask)
            and (name not in utility_classes or name in concrete_shapes)
        )
    }


class Circle(Ellipse):
    """Creates a perfect circle mask."""

    def __init__(self) -> None:
        super().__init__()


class Club(CompoundMask):
    """Creates a club shape mask like the playing card suit.

    Combines three ellipses (top and two lower) with a rectangular stem
    to form the classic club symbol.
    """

    min_size: int = 18

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)

        center = self.puzzle_size // 2
        center_offset = self.puzzle_size % 2 - 1
        ellipse_size = center - (center % 2 - 1)

        # Validate calculated dimensions
        if ellipse_size <= 0:
            raise ValueError("Invalid ellipse size.")

        # draw the 3 club circles
        top_ellipse = Ellipse(
            ellipse_size,
            ellipse_size,
            (center, center - ellipse_size // 2),
        )
        left_ellipse = Ellipse(
            ellipse_size,
            ellipse_size,
            (center - ellipse_size // 2, center + ellipse_size // 4),
            method=MaskMethod.ADDITIVE,
        )
        right_ellipse = Ellipse(
            ellipse_size,
            ellipse_size,
            (center + ellipse_size // 2, center + ellipse_size // 4),
            method=MaskMethod.ADDITIVE,
        )

        base_size = ellipse_size // 4 - (ellipse_size // 4 % 2 - 1)

        # Validate additional calculated dimensions
        if base_size <= 0:
            raise ValueError(f"Invalid base size for puzzle size {puzzle_size}.")

        base_vert = Rectangle(
            base_size,
            center,
            (center - base_size // 2 + center_offset, center),
            method=MaskMethod.ADDITIVE,
        )
        base_horz = Rectangle(
            ellipse_size,
            2,
            (center - ellipse_size // 2 + center_offset, self.puzzle_size - 2),
            method=MaskMethod.ADDITIVE,
        )

        self.masks = [top_ellipse, left_ellipse, right_ellipse, base_vert, base_horz]

        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)


class Diamond(RegularPolygon):
    """Creates a diamond (square rotated 45 degrees) mask shape."""

    def __init__(self) -> None:
        super().__init__(vertices=4, angle=90)


class Donut(CompoundMask):
    """Creates a donut (torus) shaped mask with outer circle and inner hole.

    Uses a mathematical ratio to create a visually pleasing donut shape
    with proportional inner and outer diameters.
    """

    min_size: int = 6

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)
        donut, hole = Donut.calculate_golden_donut_ratio(self.puzzle_size)

        # Validate calculated dimensions
        if donut <= 0 or hole <= 0:
            raise ValueError(f"Invalid donut dimensions for puzzle size {puzzle_size}.")
        self.masks = [
            Ellipse(donut, donut),
            Ellipse(hole, hole, method=MaskMethod.SUBTRACTIVE),
        ]
        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)

    @staticmethod
    def calculate_golden_donut_ratio(puzzle_size: int) -> tuple[int, int]:
        """Calculate proportional donut and hole sizes."""
        if puzzle_size < 6:
            raise ValueError("Puzzle size must be at least 6 for Donut shape")

        donut = puzzle_size - 1 if puzzle_size % 2 == 0 else puzzle_size
        # Ensure hole is at least 3 and not too big
        hole = max(3, int(math.pow(puzzle_size - 2, 2) // (3 * (puzzle_size - 1))))
        hole = min(hole, puzzle_size // 2)  # Don't make hole too big

        if hole % 2 == 0:
            hole += 1
        return donut, hole


class Fish(CompoundMask):
    """Creates a fish-shaped mask with an oval body and triangular tail fin.

    Combines an elliptical body with a tail fin created using overlapping ellipses
    to form a classic fish silhouette.
    """

    min_size: int = 18

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)

        center = self.puzzle_size // 2
        body_width = int(self.puzzle_size // 1.25)
        body_height = int(self.puzzle_size // 1.5 - (self.puzzle_size // 1.5 % 2 - 1))

        # Validate calculated dimensions
        if body_width <= 0 or body_height <= 0:
            raise ValueError(f"Invalid body dimensions for puzzle size {puzzle_size}.")
        body = Ellipse(
            body_width,
            body_height,
            (
                self.puzzle_size
                - body_width // 2
                - (1 if self.puzzle_size % 2 != 0 and body_width % 2 != 0 else 0),
                center,
            ),
        )
        fin = Ellipse(
            body_height,
            body_height,
            (0, center),
            method=MaskMethod.ADDITIVE,
        )

        fin_cutout = Ellipse(
            body_height,
            body_height,
            (0 - body_height // 4, center),
            method=MaskMethod.SUBTRACTIVE,
        )

        self.masks = [body, fin, fin_cutout]

        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)


class Flower(CompoundMask):
    """Creates a flower-shaped mask with four petals.

    Uses a circle divided by diagonal lines and cross separators
    to create a four-petaled flower pattern.
    """

    min_size: int = 9

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)

        flower_size = self.puzzle_size - (self.puzzle_size - 1) % 2
        center_wide_size = flower_size // 2 - (flower_size // 2 - 1) % 2

        # Validate calculated dimensions
        if flower_size <= 0 or center_wide_size <= 0:
            raise ValueError(
                f"Invalid flower dimensions for puzzle size {puzzle_size}."
            )
        flower = Ellipse(flower_size, flower_size)
        sep1 = Bitmap(method=MaskMethod.SUBTRACTIVE)
        sep2 = Bitmap(method=MaskMethod.SUBTRACTIVE)
        for i in range(flower_size):
            sep1.points.append((i, i))
            sep2.points.append((flower_size - 1 - i, i))
        center_v = Ellipse(1, center_wide_size, method=MaskMethod.SUBTRACTIVE)
        center_h = Ellipse(center_wide_size, 1, method=MaskMethod.SUBTRACTIVE)

        self.masks = [flower, sep1, sep2, center_v, center_h]

        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)


class Heart(CompoundMask):
    """Creates a heart-shaped mask like the playing card suit.

    Combines two overlapping ellipses at the top with a triangular
    bottom section to form the classic heart symbol.
    """

    min_size: int = 8

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)

        # calculate both top ellipses
        even_odd_offset = self.puzzle_size % 2
        ellipse_size = self.puzzle_size // 2 + even_odd_offset
        center_offset = 1 if self.puzzle_size % 2 != 0 and ellipse_size % 2 == 0 else 0
        ellipse_center = self.puzzle_size // 2 - ellipse_size // 2 + center_offset
        left_ellipse = Ellipse(
            width=ellipse_size,
            height=ellipse_size,
            center=(
                ellipse_center,
                ellipse_center,
            ),
        )
        right_ellipse = Ellipse(
            width=ellipse_size,
            height=ellipse_size,
            center=(
                self.puzzle_size // 2
                + ellipse_center
                - (1 if self.puzzle_size % 2 == 0 else 0),
                ellipse_center,
            ),
            method=MaskMethod.ADDITIVE,
        )
        left_ellipse.generate(self.puzzle_size)
        right_ellipse.generate(self.puzzle_size)

        # calculate the bottom half polygon
        x1 = min(x for x, _ in left_ellipse.points)
        y1 = max(
            y
            for y in range(len(left_ellipse.mask))
            if left_ellipse.mask[y][x1] == self.ACTIVE
        )
        x2 = left_ellipse.bounding_box[1][1] if left_ellipse.bounding_box else 0
        y2 = right_ellipse.bounding_box[1][1] * 2 if right_ellipse.bounding_box else 0
        x3 = right_ellipse.bounding_box[1][0] if right_ellipse.bounding_box else 0
        y3 = y1
        x4 = left_ellipse.bounding_box[1][0] if left_ellipse.bounding_box else 0
        y4 = left_ellipse.bounding_box[1][1] if left_ellipse.bounding_box else 0
        y4 = min(
            y
            for y in range(len(left_ellipse.mask))
            if left_ellipse.mask[y][x4] == self.ACTIVE
        )
        poly = Polygon(
            [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
            method=MaskMethod.ADDITIVE,
        )
        poly.generate(self.puzzle_size)

        self.masks = [left_ellipse, right_ellipse, poly]

        for mask in self.masks:
            self._apply_mask(mask)


class Hexagon(RegularPolygon):
    """Creates a regular hexagon (6-sided polygon) mask shape."""

    min_size: int = 6

    def __init__(self) -> None:
        super().__init__(vertices=6, angle=90)


class Octagon(RegularPolygon):
    """Creates a regular octagon (8-sided polygon) mask shape."""

    min_size: int = 8

    def __init__(self) -> None:
        super().__init__(vertices=8, angle=22.5)


class Pentagon(RegularPolygon):
    """Creates a regular pentagon (5-sided polygon) mask shape."""

    min_size: int = 5

    def __init__(self) -> None:
        super().__init__(vertices=5)


class Spade(CompoundMask):
    """Creates a spade shape mask like the playing card suit.

    Combines two ellipses with a triangular top section and rectangular stem
    to form the classic spade symbol.
    """

    min_size: int = 18

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)

        center = self.puzzle_size // 2
        center_offset = self.puzzle_size % 2 - 1
        ellipse_size = center - (center % 2 - 1)

        # Validate calculated dimensions
        if ellipse_size <= 0:
            raise ValueError(f"Invalid ellipse size for puzzle size {puzzle_size}.")

        # draw the two space circles
        left_ellipse = Ellipse(
            ellipse_size,
            ellipse_size,
            (center - ellipse_size // 2, center + ellipse_size // 4),
        )
        right_ellipse = Ellipse(
            ellipse_size,
            ellipse_size,
            (center + ellipse_size // 2, center + ellipse_size // 4),
            method=MaskMethod.ADDITIVE,
        )

        # draw the base
        base_size = ellipse_size // 4 - (ellipse_size // 4 % 2 - 1)

        # Validate additional calculated dimensions
        if base_size <= 0:
            raise ValueError(f"Invalid base size for puzzle size {puzzle_size}.")

        base_vert = Rectangle(
            base_size,
            center,
            (center - base_size // 2 + center_offset, center),
            method=MaskMethod.ADDITIVE,
        )
        base_horz = Rectangle(
            ellipse_size,
            2,
            (center - ellipse_size // 2 + center_offset, self.puzzle_size - 2),
            method=MaskMethod.ADDITIVE,
        )
        left_ellipse.generate(self.puzzle_size)
        right_ellipse.generate(self.puzzle_size)
        base_vert.generate(self.puzzle_size)
        base_horz.generate(self.puzzle_size)

        # calculate the top half polygon connecting the circles (will be flipped)
        # get the min y values
        left_min_y = min(y for _, y in left_ellipse.points)
        right_min_y = min(y for _, y in right_ellipse.points)
        # get the corresponding x values
        left_min_x_at_min_y = min(x for x, y in left_ellipse.points if y == left_min_y)
        right_max_x_at_min_y = max(
            x for x, y in right_ellipse.points if y == right_min_y
        )

        # calculate polygon points
        p1 = (center + center_offset, 0)
        p2 = (left_min_x_at_min_y, left_min_y)
        p3 = (center + center_offset, center)
        p4 = (right_max_x_at_min_y, right_min_y)

        poly = Polygon([p1, p2, p3, p4], method=MaskMethod.ADDITIVE)
        poly.generate(self.puzzle_size)

        self.masks = [left_ellipse, right_ellipse, base_horz, base_vert, poly]

        for mask in self.masks:
            self._apply_mask(mask)


class Star5(Star):
    """Creates a 5-pointed star mask shape."""

    min_size: int = 10

    def __init__(self) -> None:
        super().__init__()


class Star6(CompoundMask):
    """Creates a 6-pointed star (Star of David) by overlapping two triangles."""

    min_size: int = 6

    def __init__(self) -> None:
        super().__init__()
        self.masks = [
            RegularPolygon(),
            RegularPolygon(angle=180, method=MaskMethod.ADDITIVE),
        ]


class Star8(Star):
    """Creates an 8-pointed star mask shape."""

    min_size: int = 12

    def __init__(self) -> None:
        super().__init__(outer_vertices=8)


class Tree(CompoundMask):
    """Creates a tree-shaped mask with triangular top and rectangular trunk.

    Combines a triangular tree top with a proportional rectangular trunk
    to form a classic tree silhouette.
    """

    min_size: int = 10  # Conservative minimum size

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required "
                f"for a {self.__class__.__name__} mask."
            )

        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, self.ACTIVE)

        # build the tree top
        tree_top = RegularPolygon(vertices=3)
        tree_top.generate(self.puzzle_size)
        tree_top_width = tree_top.points[2][0] - tree_top.points[1][0] + 1

        # calculate trunk dimensions with better proportions
        base_trunk_width = tree_top_width // 4
        if base_trunk_width < 2:  # Ensure trunk is at least reasonably wide
            base_trunk_width = max(
                2, tree_top_width // 3
            )  # Use 1/3 instead of 1/4 for small trees

        tree_trunk_width = (
            base_trunk_width + 1 if base_trunk_width % 2 == 0 else base_trunk_width
        )
        # Ensure minimum width but don't override calculated proportional width
        tree_trunk_width = max(3, tree_trunk_width)

        # Ensure trunk height is positive with minimum
        available_height = self.puzzle_size - tree_top.points[1][1]
        tree_trunk_height = max(2, available_height)

        tree_trunk_position_x = (
            self.puzzle_size // 2 - tree_trunk_width // 2 - 1
            if self.puzzle_size % 2 == 0
            else self.puzzle_size // 2 - tree_trunk_width // 2
        )
        tree_trunk_position_y = tree_top.points[1][1]

        # Validate calculated trunk dimensions
        if tree_trunk_width <= 0 or tree_trunk_height <= 0:
            raise ValueError(f"Invalid trunk dimensions for puzzle size {puzzle_size}.")

        if tree_trunk_position_x < 0 or tree_trunk_position_x >= puzzle_size:
            raise ValueError(f"Invalid trunk position for puzzle size {puzzle_size}.")

        # build the tree trunk
        tree_trunk = Rectangle(
            width=tree_trunk_width,
            height=tree_trunk_height,
            origin=(tree_trunk_position_x, tree_trunk_position_y),
            method=MaskMethod.ADDITIVE,
        )
        tree_trunk.generate(self.puzzle_size)
        self.masks = [tree_top, tree_trunk]
        for mask in self.masks:
            self._apply_mask(mask)


class Triangle(RegularPolygon):
    """Creates a triangular mask shape."""

    def __init__(self) -> None:
        super().__init__(vertices=3)


class Square(Rectangle):
    """Creates a perfect square mask shape."""

    def __init__(self) -> None:
        # Will be properly sized during generate()
        super().__init__(width=10, height=10)

    def generate(self, puzzle_size: int) -> None:
        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        # Override to create a square that fits the puzzle
        square_size = puzzle_size - (puzzle_size % 2)  # Make it even for centering
        center_offset = (puzzle_size - square_size) // 2

        # Validate calculated dimensions
        if square_size <= 0 or center_offset < 0:
            raise ValueError(
                f"Invalid square dimensions for puzzle size {puzzle_size}."
            )
        self.points = [
            (center_offset, center_offset),
            (center_offset, center_offset + square_size - 1),
            (center_offset + square_size - 1, center_offset + square_size - 1),
            (center_offset + square_size - 1, center_offset),
        ]
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self._draw()


class Oval(Ellipse):
    """Creates an oval (elongated ellipse) mask shape."""

    def __init__(self) -> None:
        super().__init__()
        self.aspect_ratio = 1.5  # Make it wider than it is tall

    def generate(self, puzzle_size: int) -> None:
        if not isinstance(puzzle_size, int):
            raise TypeError(
                f"puzzle_size must be an integer, got {type(puzzle_size).__name__}"
            )

        if puzzle_size <= 0:
            raise ValueError(f"puzzle_size must be positive, got {puzzle_size}")

        self.puzzle_size = puzzle_size

        # Use width as the limiting factor - make it fit within puzzle bounds
        oval_width = int(puzzle_size * 0.9)  # Leave some margin for centering
        oval_height = int(oval_width / self.aspect_ratio)  # Calculate height from width

        # Validate calculated dimensions
        if oval_width <= 0 or oval_height <= 0:
            raise ValueError(f"Invalid oval dimensions for puzzle size {puzzle_size}.")

        # Center the oval
        center = (puzzle_size // 2, puzzle_size // 2)

        self.width = oval_width
        self.height = oval_height
        self.center = center

        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self.points = Ellipse.calculate_ellipse_points(
            self.width if self.width else self.puzzle_size,
            self.height if self.height else self.puzzle_size,
            self.center
            if self.center
            else (self.puzzle_size // 2, self.puzzle_size // 2),
            puzzle_size,
        )
        self._draw()


BUILTIN_MASK_SHAPES: dict[str, type[Mask]] = get_shape_objects()
