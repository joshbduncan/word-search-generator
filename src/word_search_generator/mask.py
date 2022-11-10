import math
from collections import Counter
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from PIL import Image, ImageChops

from .config import ACTIVE, INACTIVE, max_puzzle_size, min_puzzle_size
from .utils import build_puzzle


class ContrastError(Exception):
    ...


class Mask:
    """This class represents a WordSearch puzzle Mask object."""

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
        """
        self._puzzle_size: Optional[int] = None
        self.mask: List[Any] = []
        self.method: int = method
        self.static: bool = static
        self.points: List[Any] = points

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
        if self._puzzle_size != val:
            self._puzzle_size = val
            if not self.static:
                self.reset_points()

    def generate(self, puzzle_size: int) -> None:
        """Generate a mask at `puzzle_size`."""
        if self.puzzle_size != puzzle_size:
            self.puzzle_size = puzzle_size
            self.mask = build_puzzle(puzzle_size, INACTIVE)

    def show(self) -> None:
        for i, r in enumerate(self.mask):
            print(" ".join(r))

    def invert(self) -> None:
        """Invert mask. Has no effect on the `method`."""
        self.mask = [
            [ACTIVE if c == INACTIVE else INACTIVE for c in row] for row in self.mask
        ]

    def flip_horizontal(self) -> None:
        """Flip mask along the vertical axis (left to right)."""
        self.mask = [r[::-1] for r in self.mask]

    def flip_vertical(self) -> None:
        """Flip mask along the horizontal axis (top to bottom)."""
        self.mask = self.mask[::-1]

    def transpose(self) -> None:
        """Interchange each mask row with the corresponding mask column."""
        self.mask = list(map(list, zip(*self.mask)))

    def reset_points(self) -> None:
        """Remove all coordinate points from the mask."""
        self.points = []


class Bitmap(Mask):
    """This subclass of `Mask` represents Bitmap mask object."""

    def __init__(
        self, points: List[Any] = [], method: int = 1, static: bool = True
    ) -> None:
        super().__init__(method=method, static=static)
        self.points = points

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.draw()

    def draw(self) -> None:
        for x, y in self.points:
            self.mask[y][x] = ACTIVE


class RasterImage(Bitmap):
    """This subclass of `Bitmap` represents a RasterImage mask object."""

    threshold = 200

    def __init__(
        self, fp: Union[str, Path], method: int = 1, static: bool = False
    ) -> None:
        """Generate a mask from a raster image.

        Args:
            fp (Union[str, Path]): A filename (string), pathlib.Path object.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.
        """
        super().__init__(method=method, static=static)
        self.fp = fp

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.points = process_image(
            Image.open(self.fp, formats=("BMP", "JPEG", "PNG")),
            self.puzzle_size,
            RasterImage.threshold,
        )
        if not self.points:
            raise ContrastError("The provided image lacked enough contrast.")
        self.draw()

    def draw(self) -> None:
        for x, y in self.points:
            self.mask[y][x] = ACTIVE


class Ellipse(Bitmap):
    """This subclass of `Bitmap` represents a Ellipse mask object."""

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        """Generate an ellipse mask.

        Args:
            width (Optional[int], optional): Ellipse width. Defaults to None.
            height (Optional[int], optional): Ellipse height. Defaults to None.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to True.
        """
        super().__init__(method=method, static=static)
        self.width: Optional[int] = width
        self.height: Optional[int] = height

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        # if no size is specified, or size is too big, fill the puzzle
        if not self.width or self.width > puzzle_size:
            self.width = puzzle_size
        if not self.height or self.height > puzzle_size:
            self.height = puzzle_size
        self.points = calculate_ellipse_points(self.width, self.height, puzzle_size)
        self.draw()


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


class Polygon(Mask):
    """This subclass of `Mask` represents a Polygon mask object."""

    def __init__(
        self, points: List[Any] = [], method: int = 1, static: bool = True
    ) -> None:
        """Generate a polygon mask from 3 or more coordinate points.

        Note: (0, 0) coordinate is at top-left of puzzle.

        Args:
            points (list, optional): Polygon vertex coordinate points.
            Defaults to [].
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to True.
        """
        super().__init__(points=points, method=method, static=static)

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.draw()

    def draw(self) -> None:
        for points in split_polygon_points_in_half(self.points):
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self.connect_points(p1, p2)
        self.fill_shape()

    def connect_points(
        self, p1: Tuple[int, int], p2: Tuple[int, int], c: str = ACTIVE
    ) -> None:
        """Connect two points within a grid using Bresenham's line algorithm."""
        x0, y0 = p1
        x1, y1 = p2
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                self.mask[y][x] = c
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                self.mask[y][x] = c
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        self.mask[y][x] = c

    def fill_shape(self, c: str = ACTIVE) -> None:
        """Fill in the interior of a `Polygon` mask with connected vertices."""
        for y, row in enumerate(self.mask):
            for x in range(len(row)):
                if (
                    (y, x) == (0, 0)
                    or (y, x) == (0, len(row) - 1)
                    or (y, x) == (len(self.mask) - 1, 0)
                    or (y, x) == (len(self.mask) - 1, len(row) - 1)
                    or row.count(c) == 0
                ):
                    continue
                if check_if_inside(self.mask, x, y):
                    self.mask[y][x] = c


class Rectangle(Polygon):
    """This subclass of `Polygon` represents a Rectangle mask object."""

    # TODO: attempt to scale rectangle on puzzle.size change
    # TODO: make sure supplied rectangle isn't larger than puzzle

    def __init__(
        self,
        width: Optional[int],
        height: Optional[int],
        position: Tuple[int, int] = (0, 0),
        method: int = 1,
        static: bool = True,
    ) -> None:
        """Generate a rectangle mask from 4 or more coordinate points.

        Note: (0, 0) coordinate is at top-left of puzzle.

        Args:
            width (Optional[int]): Rectangle width.
            height (Optional[int]): Rectangle height.
            position (Tuple[int, int], optional): Origin coordinate point
            to draw from. Rectangles are drawn from top-left to
            bottom-right. Defaults to (0, 0).
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
        self.position: Tuple[int, int] = position

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        originX, originY = self.position
        # if no size is specified, fill the puzzle
        if not self.width or self.width + originX > puzzle_size:
            self.width = puzzle_size
        if not self.height or self.height + originY > puzzle_size:
            self.height = puzzle_size
        self.points = [
            (originX, originY),
            (originX, originY + self.height - 1),
            (originX + self.width - 1, originY + self.height - 1),
            (originX + self.width - 1, originY),
        ]
        self.draw()


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


class ConvexPolygon(Polygon):
    """This subclass of `Polygon` represents a ConvexPolygon mask object."""

    def __init__(
        self, sides: int = 3, rotation: int = 0, method: int = 1, static: bool = False
    ) -> None:
        """Generate a regular convex polygon mask with 3 or more sides.

        Note: Mask will be drawn from the puzzle center.

        Args:
            sides (int, optional): Polygon sides. Defaults to 3.
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
        self.sides = sides
        self.rotation = rotation if rotation >= 0 else 360 + rotation

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self.mask = build_puzzle(puzzle_size, INACTIVE)
        self.points = calculate_regular_convex_polygon_points(
            puzzle_size, self.sides, self.rotation
        )
        self.draw()

    def draw(self) -> None:
        for points in split_polygon_points_in_half(self.points):
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self.connect_points(p1, p2)
        self.fill_shape()


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


class Pentagon(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a Pentagon mask object."""

    def __init__(self, rotation: int = 0, method: int = 1) -> None:
        super().__init__(
            sides=5,
            rotation=rotation if rotation >= 0 else 360 + rotation,
            method=method,
        )


class Hexagon(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a Hexagon mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(sides=6, method=method, static=static)


class Octagon(ConvexPolygon):
    """This subclass of `ConvexPolygon` represents a Octagon mask object."""

    def __init__(self, method: int = 1, static: bool = False) -> None:
        super().__init__(sides=8, method=method, static=static)


# *********************************************************** #
# ******************** UTILITY FUNCTIONS ******************** #
# *********************************************************** #


def find_bounding_box(grid: List[List[str]]) -> Tuple[int, int, int, int]:
    """Find the ACTIVE area bounding box of the supplied grid."""
    size = len(grid)
    # find the top and bottom edges
    top_edge = 0
    for i in range(size):
        if grid[i].count(ACTIVE):
            top_edge = i
            break
    rows_reversed = grid[::-1]
    bottom_edge = 0
    for i in range(size):
        if rows_reversed[i].count(ACTIVE):
            bottom_edge = size - i
            break
    # find the left and right edges
    cols = list(zip(*grid))
    left_edge = 0
    for i in range(size):
        if cols[i].count(ACTIVE):
            left_edge = i
            break
    right_edge = 0
    cols_reversed = cols[::-1]
    for i in range(size):
        if cols_reversed[i].count(ACTIVE):
            right_edge = size - i
            break
    return (top_edge, left_edge, right_edge, bottom_edge)


def round_half_up(
    n: float, decimals: int = 0
) -> Union[float, Any]:  # mypy 0.95+ weirdness
    """Round numbers in a consistent and familiar format."""
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def distance(x: int, y: int, ratio: float) -> float:
    """Calculate the distance between two coordinates on a grid."""
    return math.sqrt(math.pow(y * ratio, 2) + math.pow(x, 2))


def inbounds(x: int, y: int, radius: float, ratio: float) -> bool:
    """Check is a coordinate is within a grid radius."""
    return distance(x, y, ratio) <= radius


def float_range(
    start: Union[int, float],
    stop: Optional[Union[int, float]] = None,
    step: Optional[Union[int, float]] = None,
):
    """Generate a float-based range for iteration."""
    start = float(start)
    if stop is None:
        stop = start + 0.0
        start = 0.0
    if step is None:
        step = 1.0
    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1


def calculate_ellipse_points(
    width: int, height: int, puzzle_size: int
) -> List[Tuple[int, int]]:
    """Calculate all coordinates within an ellipse."""
    width_r = width / 2
    height_r = height / 2
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
        x_offset = puzzle_size // 2 - 1
    else:
        x_offset = puzzle_size // 2
    if puzzle_size % 2 == 0 and height % 2 != 0:
        y_offset = puzzle_size // 2 - 1
    else:
        y_offset = puzzle_size // 2
    # check all points and see if they fit inside of the ellipse
    points = []
    minY = -max_pointsY / 2 + 1
    maxY = max_pointsY / 2 - 1
    minX = -max_pointsX / 2 + 1
    maxX = max_pointsX / 2 - 1
    for y in float_range(minY, maxY + 1):
        for x in float_range(minX, maxX + 1):
            if inbounds(x, y, width_r, ratio):
                points.append((int(x + x_offset), int(y + y_offset)))
    return points


def calculate_regular_convex_polygon_points(
    size: int, sides: int = 3, rotation: Union[int, float] = 0
):
    """Calculate each point/vertex of a regular convex polygon with `sides` sides."""
    size = size - 1 if size % 2 == 0 else size
    cx = cy = size // 2
    points = []
    for i in range(sides):
        x = cx - size // 2 * math.sin((((i * 360) / sides + rotation) * math.pi) / 180)
        y = cy - size // 2 * math.cos((((i * 360) / sides + rotation) * math.pi) / 180)
        points.append((int(round_half_up(x + 0.01)), int(round_half_up(y + 0.01))))
    return points


def split_polygon_points_in_half(
    points: List[Tuple[int, int]]
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Split a path of polygon points into two lists so that the
    Bresenham's line algorithm dows a better job connecting two points."""
    left_offset = len(points) // 2 + 1 if len(points) % 2 == 0 else len(points) // 2 + 2
    left_side = points[0:left_offset]
    right_offset = len(points) // 2
    right_side = [points[0]] + list(reversed(points))[:right_offset]
    return (left_side, right_side)


def follow_direction(grid: List[List[str]], d: str, x: int, y: int) -> bool:
    """Expand out from a coordinate in the four main cardinal directions
    looking for another ACTIVE point for the edge of the grid."""
    while True:
        if d.upper() == "N":
            y -= 1
            if y < 0:
                break
        if d.upper() == "S":
            y += 1
            if y > len(grid) - 1:
                break
        if d.upper() == "E":
            x += 1
            if x > len(grid) - 1:
                break
        if d.upper() == "W":
            x -= 1
            if x < 0:
                break
        if grid[y][x] == ACTIVE:
            return True
    return False


def check_if_inside(grid: List[List[str]], x: int, y: int) -> bool:
    """Determine if a coordinate is an outer edge of a shape."""
    return all(
        [
            follow_direction(grid, "N", x, y),
            follow_direction(grid, "S", x, y),
            follow_direction(grid, "E", x, y),
            follow_direction(grid, "W", x, y),
        ]
    )


# ***************************************************************** #
# ******************** IMAGE UTILITY FUNCTIONS ******************** #
# ***************************************************************** #


def normalize_rgb_values(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Clean-up any slight color differences in PIL color sampling."""
    return (
        0 if color[0] <= 3 else 255,
        0 if color[1] <= 3 else 255,
        0 if color[2] <= 3 else 255,
    )


def trim_excess(image: Image) -> Image:
    """Trim excess background pixels from around `image`."""
    w, h = image.size
    # get RGB value for each corner of image
    corners = [
        normalize_rgb_values(image.getpixel((0, 0))),
        normalize_rgb_values(image.getpixel((w - 1, 0))),
        normalize_rgb_values(image.getpixel((0, h - 1))),
        normalize_rgb_values(image.getpixel((w - 1, h - 1))),
    ]
    # count how many times each value is present
    color_count = Counter([pixel for pixel in corners]).most_common()
    # if multiple corners have the same pixel count don't trim
    if len(color_count) > 1 and color_count[0][1] == color_count[1][1]:
        return image
    else:  # set the comparison pixel to the most common value
        bg_pixel = color_count[0][0]
    # compare the original image to the excess pixels and crop
    comp = Image.new("RGB", image.size, bg_pixel)
    diff = ImageChops.difference(image, comp)
    bbox = diff.getbbox()
    return image.crop(bbox)


def process_image(image: Image, size: int, threshold: int = 200) -> Image:
    """Process `image` for bitmap mask capture."""
    # composite the image on a white background just in case it has transparency
    image = image.convert("RGBA")
    bg = Image.new("RGBA", image.size, (255, 255, 255))
    image = Image.alpha_composite(bg, image)
    # convert composite image to RGB since we don't need transparency
    image = image.convert("RGB")
    # trim excess background pixels
    image = trim_excess(image)
    # resize the image so the bitmap matches the puzzle size
    image.thumbnail((size, size), resample=0)
    # convert image to black and white
    image = image.convert("L").point(lambda px: 255 if px > threshold else 0, mode="1")
    # return all black pixels from the mask
    w, _ = image.size
    return [
        (0 if i == 0 else i % w, i // w)
        for i, px in enumerate(image.getdata())
        if px <= threshold
    ]
