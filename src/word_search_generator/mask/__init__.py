from ..utils import BoundingBox, find_bounding_box


class MaskNotGenerated(Exception):
    """Mask has not yet been generated."""

    pass


class Mask:
    """This class represents Mask object that can be applied
    to a WordSearch puzzle."""

    ACTIVE = "*"
    INACTIVE = "#"
    METHODS = [1, 2, 3]

    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        """Initialize a WordSearch puzzle mask object.

        Args:
            points (list[tuple[int, int]] | None, optional): Coordinate points
                used to build the mask. Defaults to None.
            method (int, optional): How Mask is applied to the puzzle
                (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.
            static (bool, optional): Should this mask be reapplied
                after changes to the parent puzzle size. Defaults to True.

        Notes: Bitmap points will be filled in solid, Polygon points will first
        be connected by lines in the order they are supplied and then the resulting
        shape will be filled in using a ray-casting algorithm.
        """
        self.points = points if points else []
        self.method = method
        self.static = static
        self._puzzle_size: int = 0
        self._mask: list[list[str]] = []

    @property
    def mask(self) -> list[list[str]]:
        """Mask as a 2-D array (list[list[str]])."""
        return self._mask

    @property
    def method(self) -> int:
        """Mask method."""
        return self._method

    @method.setter
    def method(self, value: int) -> None:
        """Set the Mask method.

        Args:
            method (int): How Mask is applied to the puzzle
            (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.

        Raises:
            ValueError: Must 1, 2, or 3 (see `Mask.METHODS`).
        """
        if not isinstance(value, int):
            raise TypeError("Must be an integer.")
        if isinstance(value, int) and value not in Mask.METHODS:
            raise ValueError(f"Must be one of {Mask.METHODS}")
        self._method = value

    @property
    def static(self) -> int:
        """Mask static reapplication."""
        return self._static

    @static.setter
    def static(self, value: bool) -> None:
        """Set the Mask static property.

        Args:
            val (bool): Should this mask be reapplied after
            changes to the parent puzzle size. Defaults to True.

        Raises:
            TypeError: Must be a boolean value.
        """
        if not isinstance(value, bool):
            raise TypeError("Must be a boolean value.")
        self._static = value

    @property
    def puzzle_size(self) -> int:
        """Size of the puzzle the mask will applied to. Used with the
        `generate()` to to calculate points and placement."""
        return self._puzzle_size

    @puzzle_size.setter
    def puzzle_size(self, value: int) -> None:
        """Set the `Mask.puzzle_size` value. Should match the size
        of the puzzle the mask will be applied to.

        Args:
            val (int): Size.

        Raises:
            TypeError: Must be an integer.
        """
        if not isinstance(value, int):
            raise TypeError("Must be an integer.")
        self._puzzle_size = value
        if not self.static:
            self.reset_points()

    @property
    def bounding_box(self) -> BoundingBox | None:
        """Bounding box of the masked area as a rectangle defined
        by a tuple of (top-left edge as x, y, bottom-right edge as x, y). Returned
        points may lie outside of the puzzle bounds. This property is used
        for filling mask shapes so it needs to know the actual mask bounds no
        matter where lie."""

        if not self.mask:
            return None
        return find_bounding_box(self._mask, self.ACTIVE)

    @staticmethod
    def build_mask(size: int, char: str) -> list[list[str]]:
        """Generate a 2-D array (square) of `size` filled with `char`.

        Args:
            size (int): Size of array.
            char (str, optional): Character to fill the array with.

        Returns:
            list[list[str]]: 2-D array filled will `char`.
        """
        return [[char] * size for _ in range(size)]

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size` and either fill points (`Bitmap`),
        or connect points (`Polygon`) and then fill the resulting polygon shape."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self._draw()

    def _draw(self) -> None:
        """Placeholder for custom subclass `_draw()` methods.

        Raises:
            MaskNotGenerated: Mask has not yet been generated.
        """
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        pass

    def show(self, active_only: bool = False) -> None:
        """Pretty print the mask. When `active_only` is True only the masked
        areas that lie within the bound of (0,0) and (`puzzle_size`, `puzzle_size`)
        will be shown. Used for mask creation and testing.

        Args:
            active_only (bool, optional): Only output the masked areas
                that lie within the bounds of `Mask.puzzle_size`. Used for
                mask creation and testing. Defaults to False.

        Raises:
            MaskNotGenerated: Mask has not yet been generated.
        """
        if not self.mask:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        if active_only:
            assert self.bounding_box
            min_x, min_y = self.bounding_box[0]
            max_x, max_y = self.bounding_box[1]
        else:
            ((min_x, min_y), (max_x, max_y)) = (
                (0, 0),
                (self.puzzle_size, self.puzzle_size),
            )
        for r in self.mask[min_y : max_y + 1]:
            if active_only:
                r = [c if c == self.ACTIVE else " " for c in r]
            print(" ".join(r[min_x : max_x + 1]))

    def invert(self) -> None:
        """Invert the mask. Has no effect on the mask `method`."""
        self._mask = [
            [self.ACTIVE if c == self.INACTIVE else self.INACTIVE for c in row]
            for row in self.mask
        ]

    def flip_horizontal(self) -> None:
        """Flip mask along the vertical axis (left to right)."""
        self._mask = [r[::-1] for r in self.mask]

    def flip_vertical(self) -> None:
        """Flip mask along the horizontal axis (top to bottom)."""
        self._mask = self.mask[::-1]

    def transpose(self) -> None:
        """Reverse/permute the axes of the mask."""
        self._mask = list(map(list, zip(*self.mask, strict=False)))

    def reset_points(self) -> None:
        """Reset all mask coordinate points."""
        self.points = []


class CompoundMask(Mask):
    """This class represents a subclass of the Mask object
    and allows you to generate a single mask from a set of masks."""

    def __init__(
        self, masks: list[Mask] | None = None, method: int = 1, static: bool = True
    ) -> None:
        """Initialize a WordSearch puzzle compound mask object
        built from multiple `Mask` objects.

        Args:
            masks (list[Mask] | None, optional): Masks objects used to build
                a the CompoundMask. Defaults to None.
            method (int, optional): How Mask is applied to the puzzle
                (1=Standard (Intersection), 2=Additive, 3=Subtractive). Defaults to 1.
            static (bool, optional): Should this mask be reapplied
                after changes to the parent puzzle size. Defaults to True.
        """
        super().__init__(method=method, static=static)
        self.masks = masks if masks else []

    def add_mask(self, mask: Mask) -> None:
        self.masks.append(mask)

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size` and the apply all Mask objects
        from `CompoundMask.masks` in order.

        Note: Unlike the parent `Mask` object a `CompoundMask` is initially filled
        with `self.ACTIVE`. This allows for the proper inaction between masks."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.ACTIVE)
        for mask in self.masks:
            mask.generate(self.puzzle_size)
            self._apply_mask(mask)

    def _apply_mask(self, mask: Mask) -> None:
        """Apply `Mask` to the compound mask.

        Args:
            mask (Mask): Mask to apply.

        Raises:
            MaskNotGenerated: Mask has not yet been generated.
        """
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "Please use `object.generate()` before calling `object.show()`."
            )
        for y in range(self.puzzle_size):
            for x in range(self.puzzle_size):
                if mask.method == 1:
                    if (
                        mask.mask[y][x] == self.ACTIVE
                        and self.mask[y][x] == self.ACTIVE
                    ):
                        self.mask[y][x] = self.ACTIVE
                    else:
                        self.mask[y][x] = self.INACTIVE
                elif mask.method == 2:
                    if mask.mask[y][x] == self.ACTIVE:
                        self.mask[y][x] = self.ACTIVE
                else:
                    if mask.mask[y][x] == self.ACTIVE:
                        self.mask[y][x] = self.INACTIVE


# Import all base masks shapes for easier access
# (eg. `mask.Star` vs. `mask.polygon.Star`)
from .bitmap import Bitmap as Bitmap  # noqa: F401, E402
from .bitmap import ImageMask as ImageMask  # noqa: F401, E402
from .ellipse import Ellipse as Ellipse  # noqa: F401, E402
from .polygon import Polygon as Polygon  # noqa: F401, E402
from .polygon import Rectangle as Rectangle  # noqa: F401, E402
from .polygon import RegularPolygon as RegularPolygon  # noqa: F401, E402
from .polygon import Star as Star  # noqa: F401, E402
