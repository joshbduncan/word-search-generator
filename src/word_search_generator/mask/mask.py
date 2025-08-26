from enum import IntEnum
from typing import Literal

from ..utils import BoundingBox, find_bounding_box


class MaskNotGenerated(Exception):
    """Mask has not yet been generated."""

    pass


class MaskMethod(IntEnum):
    INTERSECTION = 1
    ADDITIVE = 2
    SUBTRACTIVE = 3


MethodLiteral = Literal[1, 2, 3]


class Mask:
    """This class represents Mask object that can be applied
    to a WordSearch puzzle."""

    ACTIVE = "*"
    INACTIVE = "#"
    METHODS = [1, 2, 3]

    min_size: int | None = None

    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = True,
    ) -> None:
        """Create a WordSearch puzzle mask.

        Args:
            points: Coordinate points used to build the mask. If None, starts empty.
                - For bitmap masks, the listed points are filled in solid.
                - For polygon masks, the points are connected in order to form
                edges, and the resulting shape is filled using a ray-casting
                algorithm.
            method: How the mask is applied to the puzzle. One of
                `MaskMethod.INTERSECTION`, `MaskMethod.ADDITIVE`,
                or `MaskMethod.SUBTRACTIVE`. Defaults to `INTERSECTION`.
            static: Whether this mask should be reapplied automatically after
                the parent puzzle’s size changes. Defaults to True.
        """
        self.points = points if points else []
        self.method = method
        self.static = static
        self._puzzle_size: int = 0
        self._mask: list[list[str]] = []

    @property
    def mask(self) -> list[list[str]]:
        """Return the mask as a 2-D array of characters."""
        return self._mask

    @property
    def method(self) -> MaskMethod:
        """Return the mask method as a MaskMethod enum."""
        return self._method

    @method.setter
    def method(self, value: MaskMethod | MethodLiteral) -> None:
        """Set how the mask is applied to the puzzle.

        Args:
            value: The application mode, given either as a `MaskMethod` enum
                or its corresponding integer value:
                - `MaskMethod.INTERSECTION` (1)
                - `MaskMethod.ADDITIVE` (2)
                - `MaskMethod.SUBTRACTIVE` (3)

        Raises:
            ValueError: If the value is not a valid `MaskMethod`.
        """
        try:
            self._method = MaskMethod(value)
        except ValueError as e:
            raise ValueError(f"Must be one of {[m.value for m in MaskMethod]}") from e

    @property
    def static(self) -> bool:
        """Whether this mask should be reapplied after parent size changes."""
        return self._static

    @static.setter
    def static(self, value: bool) -> None:
        """Set whether the mask should be reapplied after size changes."""
        if not isinstance(value, bool):
            raise TypeError("Must be a boolean value.")
        self._static = value

    @property
    def puzzle_size(self) -> int:
        """Current target puzzle size (positive integer)."""
        return self._puzzle_size

    @puzzle_size.setter
    def puzzle_size(self, value: int) -> None:
        """Set the target puzzle size for this mask.

        Args:
            value: Positive integer size of the puzzle grid. Must be greater
                than zero and not smaller than `min_size` (if defined).

        Raises:
            TypeError: If `value` is not an integer.
            ValueError: If `value` is <= 0 or smaller than `min_size`.
        """
        if not isinstance(value, int):
            raise TypeError("puzzle_size must be an integer.")
        if value <= 0:
            raise ValueError("puzzle_size must be > 0.")
        if self.min_size is not None and value < self.min_size:
            raise ValueError(
                f"puzzle_size {value} is smaller than min_size {self.min_size}."
            )

        # All checks passed—now update state
        self._puzzle_size = value
        if not self.static:
            self.reset_points()

    @property
    def is_generated(self) -> bool:
        """Return True if the mask grid has been generated."""
        return bool(self._puzzle_size and self._mask)

    @property
    def bounding_box(self) -> BoundingBox | None:
        """Bounding box of the masked area.

        Returns:
            A tuple of two (x, y) coordinates:
            - top-left corner
            - bottom-right corner

            Coordinates may extend beyond the puzzle bounds. This is intentional,
            since the bounding box is used to fill mask shapes and must reflect the
            actual extent of the mask regardless of puzzle size.

        """

        if not self.mask:
            return None
        return find_bounding_box(self._mask, self.ACTIVE)

    @staticmethod
    def build_mask(size: int, char: str) -> list[list[str]]:
        """Create a square 2-D mask filled with a given character.

        Args:
            size: Positive integer width and height of the mask.
            char: Single character used to fill all cells.

        Returns:
            A `size × size` list of lists, with every entry set to `char`.
        """
        return [[char] * size for _ in range(size)]

    def generate(self, puzzle_size: int) -> None:
        """Generate a new mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self._draw()

    def _draw(self) -> None:
        """Placeholder for subclass-specific drawing logic.

        Subclasses should override this method to implement how the mask
        is drawn (e.g., filling points or polygons) after `generate()` is called.

        Raises:
            MaskNotGenerated: If the mask has not been generated yet.
        """
        if not self.puzzle_size or not self._mask:
            raise MaskNotGenerated("Mask not generated. Call `generate(size)` first.")
        pass

    def show(self, active_only: bool = False) -> None:
        """Pretty print the mask (optionally restricted to active bbox)."""
        if not self.mask:
            raise MaskNotGenerated("Mask not generated. Call `generate(size)` first.")

        if active_only:
            bbox = self.bounding_box
            if not bbox:
                # No active cells; nothing to show
                return
            (min_x, min_y), (max_x, max_y) = bbox
        else:
            min_x = min_y = 0
            max_x = max_y = self.puzzle_size - 1  # use inclusive max

        # Clamp to [0, puzzle_size-1] to prevent negative-start wrap and overshoot
        x0 = max(0, min_x)
        y0 = max(0, min_y)
        x1 = min(max_x, self.puzzle_size - 1)
        y1 = min(max_y, self.puzzle_size - 1)

        # If the bbox is completely outside, show nothing
        if x0 > x1 or y0 > y1:
            return

        for row in self.mask[y0 : y1 + 1]:
            segment = (
                row
                if not active_only
                else [c if c == self.ACTIVE else " " for c in row]
            )
            print(" ".join(segment[x0 : x1 + 1]))

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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            + f"(points={self.points}, "
            + f"method={self.method}, "
            + f"static={self.static}, "
        )


class CompoundMask(Mask):
    """This class represents a subclass of the Mask object
    and allows you to generate a single mask from a set of masks."""

    def __init__(
        self,
        masks: list[Mask] | None = None,
        method: MaskMethod | MethodLiteral = 1,
        static: bool = True,
    ) -> None:
        """Create a compound mask composed of multiple `Mask` objects.

        Args:
            masks: Child masks to combine into this `CompoundMask`.
                If None, starts with an empty list.
            method: How the compound mask is applied to the puzzle.
                One of MaskMethod.INTERSECTION, ADDITIVE, or SUBTRACTIVE.
                Defaults to INTERSECTION.
            static: Whether this mask should be reapplied automatically
                after the parent puzzle size changes. Defaults to True.
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
        """Apply a child mask to this compound mask."""
        if not self.puzzle_size:
            raise MaskNotGenerated("Mask not generated. Call `generate(size)` first.")

        if mask.method is MaskMethod.INTERSECTION:
            # self = self ∧ mask
            self._mask = [
                [
                    self.ACTIVE
                    if (a == self.ACTIVE and b == self.ACTIVE)
                    else self.INACTIVE
                    for a, b in zip(row_self, row_mask, strict=False)
                ]
                for row_self, row_mask in zip(self._mask, mask._mask, strict=False)
            ]
        elif mask.method is MaskMethod.ADDITIVE:
            # self = self ∨ mask
            self._mask = [
                [
                    self.ACTIVE
                    if (a == self.ACTIVE or b == self.ACTIVE)
                    else self.INACTIVE
                    for a, b in zip(row_self, row_mask, strict=False)
                ]
                for row_self, row_mask in zip(self._mask, mask._mask, strict=False)
            ]
        elif mask.method is MaskMethod.SUBTRACTIVE:
            # self = self ∧ ¬mask
            self._mask = [
                [
                    self.ACTIVE
                    if (a == self.ACTIVE and b != self.ACTIVE)
                    else self.INACTIVE
                    for a, b in zip(row_self, row_mask, strict=False)
                ]
                for row_self, row_mask in zip(self._mask, mask._mask, strict=False)
            ]
