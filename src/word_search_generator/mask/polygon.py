import math

from ..utils import in_bounds, round_half_up
from .mask import Mask, MaskMethod, MaskNotGenerated, MethodLiteral


class Polygon(Mask):
    """Generates polygon-shaped masks from coordinate points.

    Creates arbitrary polygon shapes by connecting a series of points
    and filling the resulting closed shape. Supports complex polygons
    with multiple vertices.
    """

    def __init__(
        self,
        points: list[tuple[int, int]] | None = None,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = True,
    ) -> None:
        """Generate a polygon mask from 3 or more coordinate points.
        The (0, 0) coordinate is at top-left of the 2-D array.

        Note: There is no need to include the origin point at the end
        of your polygon path. All paths are automatically closed by
        returning to the origin point (eg. `.points[0]`).

        Args:
            points: Polygon coordinate points. Defaults to None.
            method: How Mask is applied to the puzzle. Defaults to INTERSECTION.
            static: Should this mask be reapplied after changes to the
                parent puzzle size. Defaults to True.

        Raises:
            ValueError: If fewer than 3 points are provided.
        """
        if points and len(points) < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        super().__init__(points=points, method=method, static=static)

    @property
    def split_points(self) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
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
        """Generate a new mask at `puzzle_size`."""
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        self._draw()

    def _draw(self) -> None:  # doesn't draw evenly on second half of points (going up)
        """Connect each coordinate point within `.points` in the
        order they are listed and then fill in the resulting shape."""
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self._connect_points(p1, p2, self.ACTIVE)
        self._fill_shape(self.ACTIVE)

    def _draw_in_halves(self) -> None:
        """Starting with the first coordinate in `.points`, connect the first
        half of the coordinates, then return to the origin and connect the second
        half of the points, and then fill in the resulting shape.

        Note: Uses the `.split_points` property and seems to work with the
        Bresenham's line algorithm for some shape (eg. Stars)."""
        for points in self.split_points:
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self._connect_points(p1, p2, self.ACTIVE)
        self._fill_shape(self.ACTIVE)

    def _connect_points(self, p1: tuple[int, int], p2: tuple[int, int], c: str) -> None:
        """Connect two points within a grid using Bresenham's line algorithm.
        The line will be drawn using the single character string `c`."""
        if not self.puzzle_size:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `generate()` method."
            )
        x1, y1 = p1
        x2, y2 = p2
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
            if in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                self.mask[y][x] = c

    @staticmethod
    def point_in_polygon(
        point: tuple[int, int], polygon: list[tuple[int, int]]
    ) -> bool:
        """Ray casting algorithm to determine if a point is within a polygon.

        Args:
            point: The (x, y) coordinate to test.
            polygon: List of polygon vertices as (x, y) tuples.

        Returns:
            True if the point is inside the polygon.
        """
        x, y = point
        intersections = 0
        for i in range(len(polygon) - 1):
            x1, y1 = polygon[i]
            x2, y2 = polygon[i + 1]
            if (y < y1) != (y < y2) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                intersections += 1
        return intersections % 2 == 1

    def _fill_shape(self, c: str) -> None:
        """Fill the interior of a polygon using the single character string `c`."""
        if not self.puzzle_size or not self.bounding_box:
            raise MaskNotGenerated(
                "No puzzle size specified. Please use the `generate()` method."
            )

        # check all points within the polygon bounding box
        bbox = self.bounding_box
        min_x, min_y = bbox[0]
        max_x, max_y = bbox[1]
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                in_polygon = self.point_in_polygon(
                    (x, y), self.points + [self.points[0]]
                )
                if in_polygon and in_bounds(x, y, self.puzzle_size, self.puzzle_size):
                    self.mask[y][x] = c


class Rectangle(Polygon):
    """Generates rectangular mask shapes.

    Creates rectangular masks by defining four corner points and
    filling the resulting rectangular area.
    """

    def __init__(
        self,
        width: int,
        height: int,
        origin: tuple[int, int] | None = None,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = True,
    ) -> None:
        """Generate a rectangle polygon.

        Note: (0, 0) coordinate is at top-left of puzzle.

        Args:
            width: Rectangle width.
            height: Rectangle height.
            origin: Top-left origin point from which polygon be drawn.
                Defaults to puzzle top-left at (0, 0). Can be negative for
                mathematical positioning flexibility.
            method: How Mask is applied to the puzzle. Defaults to INTERSECTION.
            static: Should this mask be reapplied after changes to the
                parent puzzle size. Defaults to True.

        Raises:
            ValueError: If width or height are <= 0.
            TypeError: If origin is not a tuple of two coordinates.
        """
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")

        if origin is not None:
            if not isinstance(origin, tuple) or len(origin) != 2:
                raise TypeError("origin must be a tuple of two coordinates")
            if not all(isinstance(coord, int | float) for coord in origin):
                raise TypeError("origin coordinates must be numbers")

        origin_x, origin_y = origin if origin else (0, 0)
        points = [
            (origin_x, origin_y),
            (origin_x, origin_y + height - 1),
            (origin_x + width - 1, origin_y + height - 1),
            (origin_x + width - 1, origin_y),
        ]
        super().__init__(points=points, method=method, static=static)


class RegularPolygon(Polygon):
    """Generates regular polygon masks with equal sides and angles.

    Creates polygons like triangles, squares, pentagons, hexagons, etc.
    All sides have equal length and all interior angles are equal.
    """

    def __init__(
        self,
        vertices: int = 3,
        radius: int | None = None,
        center: tuple[int, int] | None = None,
        angle: float = 0.0,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = False,
    ) -> None:
        """Generate a regular polygon mask with 3 or more sides.
        All sides and internal angles will be equal.

        Args:
            vertices: Vertices (sides) of polygon (>=3). Defaults to 3.
            radius: Distance from center point to vertices. Defaults to half
                of the `puzzle_size` provided to the `.generate()` method.
            center: Center origin point from which the polygon will be calculated.
                Defaults to puzzle center. Can be negative for mathematical positioning.
            angle: Rotation angle in degrees polygon. Defaults to 0.0.
            method: How Mask is applied to the puzzle. Defaults to INTERSECTION.
            static: Should this mask be reapplied after changes to the
                parent puzzle size. Defaults to False.

        Raises:
            ValueError: If vertices < 3 or radius <= 0.
            TypeError: If center is not a tuple of two coordinates.
        """
        if vertices < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        if radius is not None and radius <= 0:
            raise ValueError("radius must be positive")

        if center is not None:
            if not isinstance(center, tuple) or len(center) != 2:
                raise TypeError("center must be a tuple of two coordinates")
            if not all(isinstance(coord, int | float) for coord in center):
                raise TypeError("center coordinates must be numbers")

        super().__init__(method=method, static=static)
        self.vertices = vertices
        self.radius = radius
        self.center = center
        self.angle = angle

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        radius = (
            self.radius
            if self.radius
            else (
                self.puzzle_size // 2 - 1
                if puzzle_size % 2 == 0
                else self.puzzle_size // 2
            )
        )
        self.points = RegularPolygon.calculate_vertices(
            self.vertices,
            radius,
            self.center if self.center else (radius, radius),
            self.angle,
        )
        self._draw()

    @staticmethod
    def calculate_vertices(
        vertices: int,
        radius: int,
        center: tuple[int, int],
        angle: float,
    ) -> list[tuple[int, int]]:
        """Calculate vertex coordinates for a regular polygon.

        Args:
            vertices: Number of polygon vertices.
            radius: Distance from center to each vertex.
            center: Center point of the polygon.
            angle: Rotation angle in degrees.

        Returns:
            List of (x, y) coordinate tuples for each vertex.
        """
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
    def cos_sin_from_degrees(degrees: float) -> tuple[float, float]:
        """Return a (cosine, sin) pair for a given angle(in degrees).
        Corrects for proper 90 degree angles."""
        degrees = degrees % 360.0
        proper_90s = {90.0: (0.0, 1.0), 180.0: (-1.0, 0), 270.0: (0, -1.0)}
        if degrees in proper_90s:
            return proper_90s[degrees]
        rad = math.radians(degrees)
        return math.cos(rad), math.sin(rad)


class Star(Polygon):
    """Generates pointed star polygon masks.

    Creates multi-pointed star shapes with alternating outer and inner
    vertices to form the classic star appearance.
    """

    def __init__(
        self,
        outer_vertices: int = 5,
        outer_radius: int | None = None,
        inner_radius: int | None = None,
        center: tuple[int, int] | None = None,
        angle: float = 0.0,
        method: MaskMethod | MethodLiteral = MaskMethod.INTERSECTION,
        static: bool = False,
    ) -> None:
        """Generate a pointed star polygon mask.

        Args:
            outer_vertices: Number of outer vertices (>=3). Defaults to 5.
            outer_radius: Distance from center point to outer vertices.
                Defaults to puzzle radius.
            inner_radius: Distance from center point to inner vertices.
                Defaults to half the puzzle radius.
            center: Center origin point from which the polygon will be calculated.
                Defaults to puzzle center. Can be negative for mathematical positioning.
            angle: Rotation angle in degrees polygon. Defaults to 0.0.
            method: How Mask is applied to the puzzle. Defaults to INTERSECTION.
            static: Should this mask be reapplied after changes to the
                parent puzzle size. Defaults to False.

        Raises:
            ValueError: If outer_vertices < 3 or radii <= 0.
            TypeError: If center is not a tuple of two coordinates.
        """
        if outer_vertices < 3:
            raise ValueError(
                "Minimum of 3 points (vertices) required to create a Polygon."
            )
        if outer_radius is not None and outer_radius <= 0:
            raise ValueError("outer_radius must be positive")
        if inner_radius is not None and inner_radius <= 0:
            raise ValueError("inner_radius must be positive")

        if center is not None:
            if not isinstance(center, tuple) or len(center) != 2:
                raise TypeError("center must be a tuple of two coordinates")
            if not all(isinstance(coord, int | float) for coord in center):
                raise TypeError("center coordinates must be numbers")

        super().__init__(method=method, static=static)
        self.outer_vertices = outer_vertices
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.center = center
        self.angle = angle

    def generate(self, puzzle_size: int) -> None:
        self.puzzle_size = puzzle_size
        self._mask = self.build_mask(self.puzzle_size, self.INACTIVE)
        puzzle_radius = (
            self.puzzle_size // 2 - 1 if puzzle_size % 2 == 0 else self.puzzle_size // 2
        )
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
        center: tuple[int, int],
        angle: float,
    ) -> list[tuple[int, int]]:
        """Calculate vertex coordinates for a star polygon.

        Args:
            outer_vertices: Number of outer star points.
            outer_radius: Distance from center to outer vertices.
            inner_radius: Distance from center to inner vertices.
            center: Center point of the star.
            angle: Rotation angle in degrees.

        Returns:
            List of (x, y) coordinate tuples alternating
                between outer and inner vertices.
        """
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
