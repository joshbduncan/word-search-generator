from typing import Any, List, Optional, Tuple

from ..config import ACTIVE, INACTIVE, max_puzzle_size, min_puzzle_size
from ..utils import find_bounding_box

PuzzleMask = List[List[str]]


class MaskNotGenerated(Exception):
    pass


class Mask:
    """This class represents a WordSearch puzzle Mask object."""

    METHODS = [1, 2, 3]

    def __init__(
        self, points: List[Any] = [], method: int = 1, static: bool = True
    ) -> None:
        """Initialize a WordSearch puzzle mask object.

        Args:
            points (List[Any], optional): Coordinate points used
            to build the mask. Defaults to [].
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to True.

        Notes: Bitmap points will be filled fill, Polygon points will be
        connected by lines in the order they are supplied.
        """
        self.points = points
        self._method = method
        self.static = static
        self._puzzle_size: Optional[int] = None
        self._mask: List[Any] = []

    @property
    def mask(self) -> List[Any]:
        """Current mask as a list of lists"""
        return self._mask

    @property
    def method(self) -> int:
        """Current mask."""
        return self._method

    @method.setter
    def method(self, val: int) -> None:
        """Set the masking method.

        Args:
            method (int): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be one of `Mask.METHODS`.
        """
        if not isinstance(val, int):
            raise TypeError("Method must be an integer.")
        if val not in Mask.METHODS:
            raise ValueError(f"Method must be one of {Mask.METHODS}")
        self.method = val

    @property
    def puzzle_size(self) -> Optional[int]:
        """Size (in characters) of the puzzle mask is being applied to."""
        return self._puzzle_size

    @puzzle_size.setter
    def puzzle_size(self, val: int) -> None:
        """Set the mask puzzle size. All puzzles are square.

        Args:
            val (int): Size in characters (grid squares).

        Raises:
            TypeError: Must be an integer.
            ValueError: Must be greater than `config.min_puzzle_size` and
            less than `config.max_puzzle_size`.
        """
        if not isinstance(val, int):
            raise TypeError("Puzzle size must be an integer.")
        if not min_puzzle_size <= val <= max_puzzle_size:
            raise ValueError(
                f"Puzzle size must be >= {min_puzzle_size}"
                + f" and <= {max_puzzle_size}"
            )
        self._puzzle_size = val
        if not self.static:
            self.reset_points()

    @property
    def bounding_box(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Bounding box of the masked area as a rectangle defined
        by a Tuple of (top-left edge as x, y, bottom-right edge as x, y)."""
        if not self.points:
            return None
        min_x, min_y = self.points[0]
        max_x, max_y = self.points[0]
        for x, y in self.points:
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y
        return ((min_x, min_y), (max_x, max_y))

    @staticmethod
    def build_mask(size: int, char: str = INACTIVE) -> PuzzleMask:
        return [[char] * size for _ in range(size)]

    def generate(self, puzzle_size: int) -> None:
        """Generate a mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(puzzle_size)
        self._draw()

    def _draw(self) -> None:
        """Placeholder for custom subclass `_draw()` method."""
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        pass

    def show(self, active_only: bool = False) -> None:
        if not self.puzzle_size or not self.bounding_box:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        bbox = (
            self.bounding_box
            if active_only
            else ((0, 0), (self.puzzle_size, self.puzzle_size))
        )
        min_x, min_y = bbox[0]
        max_x, max_y = bbox[1]

        # adjust for shapes with points out of the puzzle bounds
        if active_only:
            if min_x < 0:
                min_x = 0
            if max_x > self.puzzle_size:
                max_x = self.puzzle_size
            if min_y < 0:
                min_y = 0
            if max_y > self.puzzle_size:
                max_y = self.puzzle_size

        for r in self.mask[min_y : max_y + 1]:  # noqa: E203
            if active_only:
                r = [c if c == ACTIVE else " " for c in r]
            print(" ".join(r[min_x : max_x + 1]))

    def invert(self) -> None:
        """Invert mask. Has no effect on the `method`."""
        self._mask = [
            [ACTIVE if c == INACTIVE else INACTIVE for c in row] for row in self.mask
        ]

    def flip_horizontal(self) -> None:
        """Flip mask along the vertical axis (left to right)."""
        self._mask = [r[::-1] for r in self.mask]

    def flip_vertical(self) -> None:
        """Flip mask along the horizontal axis (top to bottom)."""
        self._mask = self.mask[::-1]

    def transpose(self) -> None:
        """Interchange each mask row with the corresponding mask column."""
        self._mask = list(map(list, zip(*self.mask)))

    def reset_points(self) -> None:
        """Remove all coordinate points from the mask."""
        self.points = []


class CompoundMask(Mask):
    """This class represents a WordSearch puzzle CompoundMask object."""

    def __init__(
        self, masks: List[Any] = [], method: int = 1, static: bool = True
    ) -> None:
        """Initialize a WordSearch puzzle compound mask object
        built from multiple `Mask` objects.

        Args:
            masks (List[Any], optional): Masks used to build a
            compound path. Defaults to [].
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to True.
        """
        super().__init__(method=method, static=static)
        self._masks = masks

    @property
    def bounding_box(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Bounding box of the masked area as a rectangle defined
        by a Tuple of (top-left edge as x, y, bottom-right edge as x, y).

        Note: This is a special implementation of the `bounding.box` property
        in use just for the `CompoundMask` object. Normally the `bounding_box`
        property on a mask is not confined to the puzzle bounds since it is mainly
        used in calculation for filling the shapes. Since a `CompoundMask` is
        really just a collection of `Masks` the `bounding_box` is limited by the
        puzzle bounds."""
        return find_bounding_box(self._mask)

    def add_mask(self, mask: Mask) -> None:
        self._masks.append(mask)

    def generate(self, puzzle_size: int) -> None:
        """Generate a mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(puzzle_size, ACTIVE)
        for mask in self._masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)

    def _apply_mask(self, mask: Mask) -> None:
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        for y in range(self.puzzle_size):
            for x in range(self.puzzle_size):
                if mask.method == 1:
                    if mask.mask[y][x] == ACTIVE and self.mask[y][x] == ACTIVE:
                        self.mask[y][x] = ACTIVE
                    else:
                        self.mask[y][x] = INACTIVE
                elif mask.method == 2:
                    if mask.mask[y][x] == ACTIVE:
                        self.mask[y][x] = ACTIVE
                    elif self.mask[y][x] != ACTIVE:
                        self.mask[y][x] = INACTIVE
                else:
                    if mask.mask[y][x] == ACTIVE:
                        self.mask[y][x] = INACTIVE


# make masks objects easier to access (eg. `mask.Star` vs. `mask.polygon.Star`)
from .bitmap import Bitmap, Image  # noqa: F401, E402
from .ellipse import Ellipse  # noqa: F401, E402
from .polygon import Polygon, Rectangle, RegularPolygon, Star  # noqa: F401, E402
