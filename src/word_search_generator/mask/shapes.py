import inspect
import math
import sys
from typing import Tuple

from ..config import ACTIVE
from . import CompoundMask, Mask
from .ellipse import Ellipse
from .polygon import RegularPolygon, Star


def get_shape_objects():
    """Return all built-in shape objects from this file"""
    # {key:value for (key,value) in dictonary.items()}
    return [
        name
        for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
        if obj.__module__ is __name__
    ]


class Circle(Ellipse):
    def __init__(self) -> None:
        super().__init__()


class Diamond(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=4, angle=90)


class Donut(CompoundMask):
    def __init__(self) -> None:
        super().__init__()

    def generate(self, puzzle_size: int) -> None:
        """Generate a mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(puzzle_size, ACTIVE)
        donut, hole = Donut.calculate_golden_donut_ratio(self.puzzle_size)
        self._masks = [
            Ellipse(donut, donut),
            Ellipse(hole, hole, method=3),
        ]
        for mask in self._masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)

    @staticmethod
    def calculate_golden_donut_ratio(puzzle_size: int) -> Tuple[int, int]:
        donut = puzzle_size - 1 if puzzle_size % 2 == 0 else puzzle_size
        hole = int(math.pow(puzzle_size - 2, 2) // (3 * (puzzle_size - 1)))
        if hole % 2 == 0:
            hole += 1
        return donut, hole


class Hexagon(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=6, angle=90)


class Octagon(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=8, angle=22.5)


class Pentagon(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=5)


class Star6Points(CompoundMask):
    def __init__(self) -> None:
        super().__init__()
        self._masks = [
            (RegularPolygon()),
            (RegularPolygon(angle=180, method=2)),
        ]


class Star5Points(Star):
    def __init__(self) -> None:
        super().__init__()


class Triangle(RegularPolygon):
    def __init__(self) -> None:
        super().__init__(vertices=3)


BUILTIN_SHAPES = get_shape_objects()
