import inspect
import math
import sys
from typing import Tuple

from ..config import ACTIVE
from . import Bitmap, CompoundMask
from .ellipse import Ellipse
from .polygon import Polygon, Rectangle, RegularPolygon, Star


def get_shape_objects():
    """Return all built-in shape objects from this file"""
    return [
        name
        for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
        if obj.__module__ is __name__
    ]


class Circle(Ellipse):
    def __init__(self) -> None:
        super().__init__()


class Club(CompoundMask):
    min_size = 18

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required \
for a {self.__class__.__name__} mask."
            )

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)

        center = self.puzzle_size // 2
        center_offset = self.puzzle_size % 2 - 1
        ellipse_size = center - (center % 2 - 1)

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
            method=2,
        )
        right_ellipse = Ellipse(
            ellipse_size,
            ellipse_size,
            (center + ellipse_size // 2, center + ellipse_size // 4),
            method=2,
        )

        base_size = ellipse_size // 4 - (ellipse_size // 4 % 2 - 1)
        base_vert = Rectangle(
            base_size,
            center,
            (center - base_size // 2 + center_offset, center),
            method=2,
        )
        base_horz = Rectangle(
            ellipse_size,
            2,
            (center - ellipse_size // 2 + center_offset, self.puzzle_size - 2),
            method=2,
        )

        self.masks = [top_ellipse, left_ellipse, right_ellipse, base_vert, base_horz]

        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)


class Diamond(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=4, angle=90)


class Donut(CompoundMask):
    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)
        donut, hole = Donut.calculate_golden_donut_ratio(self.puzzle_size)
        self.masks = [
            Ellipse(donut, donut),
            Ellipse(hole, hole, method=3),
        ]
        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)

    @staticmethod
    def calculate_golden_donut_ratio(puzzle_size: int) -> Tuple[int, int]:
        donut = puzzle_size - 1 if puzzle_size % 2 == 0 else puzzle_size
        hole = int(math.pow(puzzle_size - 2, 2) // (3 * (puzzle_size - 1)))
        if hole % 2 == 0:
            hole += 1
        return donut, hole


class Fish(CompoundMask):
    min_size = 18

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required \
for a {self.__class__.__name__} mask."
            )

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)

        center = self.puzzle_size // 2
        body_width = int(self.puzzle_size // 1.25)
        body_height = int(self.puzzle_size // 1.5 - (self.puzzle_size // 1.5 % 2 - 1))
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
            method=2,
        )

        fin_cutout = Ellipse(
            body_height,
            body_height,
            (0 - body_height // 4, center),
            method=3,
        )

        self.masks = [body, fin, fin_cutout]

        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)


class Flower(CompoundMask):
    min_size = 9

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required \
for a {self.__class__.__name__} mask."
            )

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)

        flower_size = self.puzzle_size - (self.puzzle_size - 1) % 2
        center_wide_size = flower_size // 2 - (flower_size // 2 - 1) % 2
        flower = Ellipse(flower_size, flower_size)
        sep1 = Bitmap(method=3)
        sep2 = Bitmap(method=3)
        for i in range(flower_size):
            sep1.points.append((i, i))
            sep2.points.append((flower_size - 1 - i, i))
        center_v = Ellipse(1, center_wide_size, method=3)
        center_h = Ellipse(center_wide_size, 1, method=3)

        self.masks = [flower, sep1, sep2, center_v, center_h]

        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)


class Heart(CompoundMask):
    min_size = 8

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required \
for a {self.__class__.__name__} mask."
            )

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)

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
            method=2,
        )
        left_ellipse.generate(self.puzzle_size)
        right_ellipse.generate(self.puzzle_size)

        # calculate the bottom half polygon
        x1 = min(x for x, _ in left_ellipse.points)
        y1 = max(
            y
            for y in range(len(left_ellipse.mask))
            if left_ellipse.mask[y][x1] == ACTIVE
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
            if left_ellipse.mask[y][x4] == ACTIVE
        )
        poly = Polygon(
            [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
            method=2,
        )
        poly.generate(self.puzzle_size)

        self.masks = [left_ellipse, right_ellipse, poly]

        for mask in self.masks:
            self._apply_mask(mask)


class Hexagon(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=6, angle=90)


class Octagon(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=8, angle=22.5)


class Pentagon(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=5)


class Spade(CompoundMask):
    min_size = 18

    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        if puzzle_size < self.min_size:
            raise ValueError(
                f"Puzzle size >= {self.min_size} required \
for a {self.__class__.__name__} mask."
            )

        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)

        center = self.puzzle_size // 2
        center_offset = self.puzzle_size % 2 - 1
        ellipse_size = center - (center % 2 - 1)

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
            method=2,
        )

        # draw the base
        base_size = ellipse_size // 4 - (ellipse_size // 4 % 2 - 1)
        base_vert = Rectangle(
            base_size,
            center,
            (center - base_size // 2 + center_offset, center),
            method=2,
        )
        base_horz = Rectangle(
            ellipse_size,
            2,
            (center - ellipse_size // 2 + center_offset, self.puzzle_size - 2),
            method=2,
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

        poly = Polygon([p1, p2, p3, p4], method=2)
        poly.generate(self.puzzle_size)

        self.masks = [left_ellipse, right_ellipse, base_horz, base_vert, poly]

        for mask in self.masks:
            self._apply_mask(mask)


class Star5(Star):
    def __init__(self) -> None:
        super().__init__()


class Star6(CompoundMask):
    def __init__(self) -> None:
        super().__init__()
        self.masks = [
            (RegularPolygon()),
            (RegularPolygon(angle=180, method=2)),
        ]


class Star8(Star):
    def __init__(self) -> None:
        super().__init__(outer_vertices=8)


class Tree(CompoundMask):
    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(puzzle_size, ACTIVE)
        # build the tree top
        tree_top = RegularPolygon(vertices=3)
        tree_top.generate(self.puzzle_size)
        tree_top_width = tree_top.points[2][0] - tree_top.points[1][0] + 1
        # calculate the tree trunk size and position
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
        # build the tree trunk
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
            self._apply_mask(mask)


class Triangle(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=3)


BUILTIN_MASK_SHAPES = get_shape_objects()
