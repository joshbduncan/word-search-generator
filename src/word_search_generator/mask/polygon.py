import math
from typing import Any, List, Optional, Tuple

from ..config import ACTIVE
from ..utils import in_bounds, round_half_up
from . import Mask, MaskNotGenerated


class Polygon(Mask):
    """This subclass of `Mask` represents a Polygon mask object."""

    def __init__(
        self, points: List[Any] = [], method: int = 1, static: bool = True
    ) -> None:
        """Generate a polygon mask from 3 or more coordinate points.

        Note: (0, 0) coordinate is at top-left of puzzle.
        Note: The polygon path will be automatically close if you do not
        return to the origin at the last point in your list.

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
        if points and len(points) < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(points=points, method=method, static=static)

    @property
    def split_points(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Polygon points path split in half for better drawing
        performance with Bresenham's line algorithm."""
        left_offset = (
            len(self.points) // 2 + 1
            if len(self.points) % 2 == 0
            else len(self.points) // 2 + 2
        )
        left_side = self.points[0:left_offset]
        right_offset = len(self.points) // 2
        right_side = [self.points[0]] + list(reversed(self.points))[:right_offset]
        return left_side, right_side

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(self.puzzle_size)
        self._draw()

    # doesn't draw evenly on second half pf point (going up)
    def _draw(self) -> None:
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self._connect_points(p1, p2)
        self._fill_shape()

    def _draw_in_halves(self) -> None:
        for points in self.split_points:
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self._connect_points(p1, p2)
        self._fill_shape()

    def _connect_points(
        self, p1: Tuple[int, int], p2: Tuple[int, int], c: str = ACTIVE
    ) -> None:
        """Connect two points within a grid using Bresenham's line algorithm."""
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `Polygon.generate()` method."
            )
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
                if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self.mask[y][x] = c

    def _fill_shape(self, c: str = ACTIVE) -> None:
        """Fill interior of a `Polygon` mask with connected vertices."""

        def ray_casting(point, polygon):
            x, y = point
            ct = 0
            for i in range(len(polygon) - 1):
                x1, y1 = polygon[i]
                x2, y2 = polygon[i + 1]
                if (y < y1) != (y < y2) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    ct += 1
            return ct % 2 == 1

        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `Polygon.generate()` method."
            )

        if not self.bounding_box:
            return

        # check all points within the polygon bounding box
        bbox = self.bounding_box
        min_x, min_y = bbox[0]
        max_x, max_y = bbox[1]
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                in_polygon = ray_casting((x, y), self.points + [self.points[0]])
                if in_polygon and in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c


class Rectangle(Polygon):
    """This subclass of `Polygon` represents a Rectangle mask object."""

    def __init__(
        self,
        width: int,
        height: int,
        origin: Optional[Tuple[int, int]] = None,
        method: int = 1,
        static: bool = True,
    ) -> None:
        """Generate a rectangle polygon.

        Note: (0, 0) coordinate is at top-left of puzzle.

        Args:
            width (int): Rectangle width.
            height (int): Rectangle height.
            origin (Tuple[int, int], optional): Top-left origin point from
            which polygon be drawn. Defaults to puzzle top-left at (0, 0).
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to True.
        """
        originX, originY = origin if origin else (0, 0)
        points = [
            (originX, originY),
            (originX, originY + height - 1),
            (originX + width - 1, originY + height - 1),
            (originX + width - 1, originY),
        ]
        super().__init__(points=points, method=method, static=static)


class RegularPolygon(Polygon):
    """This subclass of `Polygon` represents a RegularPolygon mask object."""

    def __init__(
        self,
        vertices: int = 3,
        radius: Optional[int] = None,
        center: Optional[Tuple[int, int]] = None,
        angle: float = 0.0,
        method: int = 1,
        static: bool = False,
    ) -> None:
        """Generate a regular polygon mask with 3 or more sides.
        All sides and internal angles will be equal.

        Args:
            vertices (int, optional): Vertices (sides) of polygon (>=3).
            Defaults to 3.
            radius (Optional[int], optional): Distance from center point to vertices.
            Defaults to `puzzle_size` // 2.
            center (Optional[Tuple[int, int]], optional): Center origin point
            from which the polygon will be calculated. Defaults to puzzle center.
            angle (float, optional): Rotation angle in degrees polygon.
            Defaults to 0.0.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.

        Raises:
            ValueError: Polygon vertices must be >=3.
        """
        if vertices < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(method=method, static=static)
        self.vertices = vertices
        self.radius = radius
        self.center = center
        self.angle = angle

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(self.puzzle_size)
        even = puzzle_size % 2 == 0
        puzzle_radius = self.puzzle_size // 2 - 1 if even else self.puzzle_size // 2
        puzzle_center = (puzzle_radius, puzzle_radius)
        self.points = RegularPolygon.calculate_vertices(
            self.vertices,
            self.radius if self.radius else puzzle_radius,
            self.center if self.center else puzzle_center,
            self.angle,
        )
        self._draw()

    @staticmethod
    def calculate_vertices(
        vertices: int,
        radius: int,
        center: Tuple[int, int],
        angle: float,
    ):
        points = []
        cx, cy = center
        angle_step = 360.0 / vertices
        angle = angle - 90  # rotated -90 so polygons are oriented North
        for _ in range(vertices):
            x, y = RegularPolygon.cos_sin_from_degrees(angle)
            points.append(
                (
                    int(round_half_up(x * radius + cx)),
                    int(round_half_up(y * radius + cy)),
                )
            )
            angle += angle_step
        return points

    @staticmethod
    def cos_sin_from_degrees(degrees: float) -> Tuple[float, float]:
        """Return a (cosine, sin) pair for a given angle(in degrees).
        Corrects for proper 90 degree angles."""
        degrees = degrees % 360.0
        proper_90s = {90.0: (0.0, 1.0), 180.0: (-1.0, 0), 270.0: (0, -1.0)}
        if degrees in proper_90s:
            return proper_90s[degrees]
        rad = math.radians(degrees)
        return math.cos(rad), math.sin(rad)


class Star(Polygon):
    """This subclass of `Polygon` represents a Star mask object."""

    def __init__(
        self,
        outer_vertices: int = 5,
        outer_radius: Optional[int] = None,
        inner_radius: Optional[int] = None,
        center: Optional[Tuple[int, int]] = None,
        angle: float = 0.0,
        method: int = 1,
        static: bool = False,
    ) -> None:
        """Generate a pointed star polygon mask.

        Args:
            outer_vertices (int, optional): Number of outer vertices (>=3).
            Defaults to 5.
            outer_radius (Optional[int], optional): Distance from center point
            to outer vertices. Defaults to None.
            inner_radius (Optional[int], optional): Distance from center point
            to inner vertices. Defaults to None.
            center (Optional[Tuple[int, int]], optional): Center origin point
            from which the polygon will be calculated. Defaults to puzzle center.
            angle (float, optional): Rotation angle in degrees polygon.
            Defaults to 0.0.
            method (int, optional): Masking method. Defaults to 1.
                1. Standard (Intersection)
                2. Additive
                3. Subtractive
            static (bool, optional): Mask should not be recalculated
            and reapplied after a `puzzle_size` change. Defaults to False.

        Raises:
            ValueError: Polygon outer vertices must be >=3.
        """
        if outer_vertices < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(method=method, static=static)
        self.outer_vertices = outer_vertices
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.center = center
        self.angle = angle

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = Mask.build_mask(self.puzzle_size)
        even = self.puzzle_size % 2 == 0
        puzzle_radius = self.puzzle_size // 2 - 1 if even else self.puzzle_size // 2
        puzzle_center = (puzzle_radius, puzzle_radius)
        self.points = Star.calculate_vertices(
            self.outer_vertices,
            self.outer_radius if self.outer_radius else puzzle_radius,
            self.inner_radius if self.inner_radius else puzzle_radius // 2,
            self.center if self.center else puzzle_center,
            self.angle,
        )
        self._draw_in_halves()

    @staticmethod
    def calculate_vertices(
        outer_vertices: int,
        outer_radius: int,
        inner_radius: int,
        center: Tuple[int, int],
        angle: float,
    ):
        points = []
        cx, cy = center
        angle_step = 180.0 / outer_vertices
        angle = angle - 90  # rotated -90 so polygons are oriented North
        for _ in range(outer_vertices):
            # calculate outer point/vertex
            x, y = RegularPolygon.cos_sin_from_degrees(angle)
            points.append(
                (
                    int(round_half_up(x * outer_radius + cx)),
                    int(round_half_up(y * outer_radius + cy)),
                )
            )
            angle += angle_step
            # calculate inner point/vertex
            x, y = RegularPolygon.cos_sin_from_degrees(angle)
            points.append(
                (
                    int(round_half_up(x * inner_radius + cx)),
                    int(round_half_up(y * inner_radius + cy)),
                )
            )
            angle += angle_step
        return points
