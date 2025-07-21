#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two-dimensional geometric shapes module.

This module provides classes for working with various 2D geometric shapes:
- Point2D: Represents a point with x and y coordinates
- Line2D: Represents a line segment between two points
- Triangle2D: Represents a triangle defined by three points
- Quadrilateral2D: Represents a quadrilateral defined by four points
- Polygon2D: Represents a polygon defined by a list of vertices

All shapes provide methods for common geometric operations such as:
- Area calculation
- Checking if a point is contained within a shape

The module emphasizes performance by pre-calculating properties where appropriate
and numerical stability in floating-point calculations.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from math import acos, atan2, cos, pi, sin, sqrt
from typing import List, Optional, Sequence

from euler.types import EulerError

# Epsilon for floating point comparisons
epsilon: float = 1e-10


class ShapeError(EulerError):
    """Exception raised for errors in geometric shape validation or creation.

    This exception is raised when attempting to create invalid geometric shapes,
    such as a triangle with two points, a line with coincident points,
    or a non-simple quadrilateral.
    """
    pass


class TriangleType(Enum):
    """Enumeration of triangle types.

    Represents different specialized types of triangles:
    - EQUILATERAL: All sides equal in length
    - ISOSCELES: Two sides equal in length
    - SCALENE: No sides equal in length
    - RIGHT: Contains a right angle (90 degrees)
    - ACUTE: All angles less than 90 degrees
    - OBTUSE: One angle greater than 90 degrees

    Note: The angle-based classifications (RIGHT, ACUTE, OBTUSE) can be combined
    with the side-based classifications (EQUILATERAL, ISOSCELES, SCALENE).
    For example, a triangle can be both RIGHT and ISOSCELES.
    """
    # Side-based classifications
    EQUILATERAL = auto()  # All sides equal
    ISOSCELES = auto()  # Two sides equal
    SCALENE = auto()  # No sides equal

    # Angle-based classifications
    RIGHT = auto()  # Has a right angle (90°)
    ACUTE = auto()  # All angles < 90°
    OBTUSE = auto()  # One angle > 90°


class QuadrilateralType(Enum):
    """Enumeration of quadrilateral types.

    Represents the different specialized types of quadrilaterals:
    - GENERAL: Any four-sided polygon
    - TRAPEZOID: A quadrilateral with exactly one pair of parallel sides
    - PARALLELOGRAM: A quadrilateral with opposite sides parallel
    - RHOMBUS: A parallelogram with all sides equal in length
    - RECTANGLE: A parallelogram with all angles equal to 90 degrees
    - SQUARE: A rectangle with all sides equal in length
    - KITE: A quadrilateral with two pairs of adjacent sides equal in length
    """
    GENERAL = auto()  # Any four-sided polygon
    TRAPEZOID = auto()  # One pair of parallel sides
    PARALLELOGRAM = auto()  # Both pairs of opposite sides parallel
    RHOMBUS = auto()  # Parallelogram with all sides equal
    RECTANGLE = auto()  # Parallelogram with right angles
    SQUARE = auto()  # Rectangle with all sides equal
    KITE = auto()  # Two pairs of adjacent sides equal


class PolygonType(Enum):
    """Enumeration of polygon types based on sides and angles properties.

    The enum values are ordered from most general to most specific.
    """
    GENERAL = auto()  # General polygon with no special properties
    CONCAVE = auto()  # Non-convex polygon
    CONVEX = auto()  # Convex polygon with no special side/angle properties
    EQUILATERAL = auto()  # All sides equal, angles may differ
    EQUIANGULAR = auto()  # All angles equal, sides may differ
    REGULAR = auto()  # All sides equal and all angles equal


def from_points_str(comma_seperated_points_str: str) -> Shape2D:
    try:
        points: List[int] = list(map(int, comma_seperated_points_str.split(',')))
    except ValueError:
        raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Ensure all values are integers.')
    else:
        if (len_points := len(points)) < 2:
            raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Expected at least two values.')
        if len_points % 2 != 0:
            raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Expected an even number of values.')
    if len(points) == 2:
        return Point2D(x=points[0], y=points[1])
    elif len(points) == 4:
        return Line2D(a=Point2D(x=points[0], y=points[1]), b=Point2D(x=points[2], y=points[3]))
    elif len(points) == 6:
        return Triangle2D(a=Point2D(x=points[0], y=points[1]),
                          b=Point2D(x=points[2], y=points[3]),
                          c=Point2D(x=points[4], y=points[5]))
    elif len(points) == 8:
        return Quadrilateral2D(a=Point2D(x=points[0], y=points[1]), b=Point2D(x=points[2], y=points[3]),
                               c=Point2D(x=points[4], y=points[5]), d=Point2D(x=points[6], y=points[7]))
    else:
        return Polygon2D(vertices=tuple(Point2D(x=points[i], y=points[i + 1]) for i in range(0, len(points), 2)))


@dataclass(frozen=True, slots=True, kw_only=True)
class Shape2D(ABC):
    @property
    @abstractmethod
    def area(self) -> float:
        """Calculate and return the area of the shape."""
        pass

    @abstractmethod
    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is contained within the shape."""
        pass


@dataclass(frozen=True, slots=True, kw_only=True)
class Point2D(Shape2D):
    """A class representing a point in 2D space."""
    x: float | int
    y: float | int

    @property
    def area(self) -> float:
        return 0.0

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is equal to the current point."""
        return self == point

    def __add__(self, other: Point2D) -> Point2D:
        """Add two points together."""
        return Point2D(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        """Subtract two points."""
        return Point2D(x=self.x - other.x, y=self.y - other.y)

    def distance_to(self, other: Point2D) -> float:
        """Calculate Euclidean distance between two points."""
        distance: float = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        return distance

    def midpoint(self, other: Point2D) -> Point2D:
        """Find midpoint between two points."""
        return Point2D(x=(self.x + other.x) / 2, y=(self.y + other.y) / 2)

    def as_polar(self, origin: Optional[Point2D] = None) -> PolarPoint2D:
        """Convert the point to polar coordinates relative to the given origin.

        Args:
            origin: The reference point for the polar coordinate system.
                    If None, (0, 0) is used.

        Returns:
            A PolarPoint2D object with r (radial distance) and theta (angle in radians in range [-π, π))
        """
        # Use (0, 0) as default origin
        ox = 0 if origin is None else origin.x
        oy = 0 if origin is None else origin.y

        # Calculate relative coordinates
        dx = self.x - ox
        dy = self.y - oy

        # Calculate radius (distance from origin)
        radius = (dx ** 2 + dy ** 2) ** 0.5

        # Calculate angle in radians in range [-π, π)
        angle = atan2(dy, dx)

        return PolarPoint2D(r=radius, theta=angle)

    @staticmethod
    def sort_points(points: Sequence[Point2D], reverse: bool = False) -> List[Point2D]:
        """Sort points around their centroid in counter-clockwise order."""
        if not points:
            return []

        # Calculate center point (centroid)
        n = len(points)
        center_x: float = sum(p.x for p in points) / n
        center_y: float = sum(p.y for p in points) / n
        centroid = Point2D(x=center_x, y=center_y)

        # Define a custom sorting key that converts [-π, π) to [0, 2π) for proper sorting
        def angle_key(p: Point2D) -> float:
            angle = p.as_polar(centroid).theta
            # Convert from [-π, π) to [0, 2π) range for correct sorting order
            return angle if angle >= 0 else angle + 2 * pi

        # Sort points based on their polar angle relative to the centroid
        return sorted(points, key=angle_key, reverse=reverse)


@dataclass(frozen=True, slots=True, kw_only=True)
class PolarPoint2D(Shape2D):
    """A class representing a point in polar coordinates"""
    r: float
    theta: float

    @property
    def area(self) -> float:
        return 0.0

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is equal to the current point."""
        return self.as_cartesian() == point

    def __add__(self, other: PolarPoint2D) -> PolarPoint2D:
        """Add two polar points together."""
        return PolarPoint2D(r=self.r + other.r, theta=self.theta + other.theta)

    def __sub__(self, other: PolarPoint2D) -> PolarPoint2D:
        """Subtract two polar points together."""
        return PolarPoint2D(r=self.r - other.r, theta=self.theta - other.theta)

    def distance_to(self, other: PolarPoint2D) -> float:
        """Calculate Euclidean distance between two polar points."""
        distance: float = ((self.r - other.r) ** 2 + (self.theta - other.theta) ** 2) ** 0.5
        return distance

    def as_cartesian(self) -> Point2D:
        """Convert polar coordinates to Cartesian coordinates.

        Returns:
            A Point2D object with Cartesian coordinates.
        """
        return Point2D(x=self.r * cos(self.theta), y=self.r * sin(self.theta))


@dataclass(frozen=True, slots=True, kw_only=True)
class Line2D(Shape2D):
    """A class representing a line in 2D space."""
    a: Point2D
    b: Point2D

    @property
    def area(self) -> float:
        return 0.0

    def __post_init__(self) -> None:
        if len({self.a, self.b}) != 2:
            raise ShapeError(f'Invalid line points: {self.a}, {self.b}')

    @property
    def length(self) -> float:
        """Calculate the Euclidean distance between the two points of the line."""
        return self.a.distance_to(self.b)

    def slope(self) -> float:
        """Calculate the slope of the line."""
        if self.a.x == self.b.x:  # Vertical line
            return float('inf')
        return (self.b.y - self.a.y) / (self.b.x - self.a.x)

    def y_intercept(self) -> float | None:
        """Calculate the y-intercept of the line (where the line crosses the y-axis)."""
        if self.a.x == self.b.x:  # Vertical line
            return float('inf') if self.a.x == 0 else None
        return self.a.y - self.slope() * self.a.x

    def x_intercept(self) -> float | None:
        """Calculate the x-intercept of the line (where the line crosses the x-axis)."""
        if self.a.y == self.b.y:  # Horizontal line
            return float('inf') if self.a.y == 0 else None
        return self.a.x - self.a.y / self.slope()

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point lies on the line segment."""
        # Check if point is within the bounding box of the line segment
        if not (min(self.a.x, self.b.x) <= point.x <= max(self.a.x, self.b.x) and
                min(self.a.y, self.b.y) <= point.y <= max(self.a.y, self.b.y)):
            return False

        # For vertical or horizontal lines, simple check is sufficient
        if self.a.x == self.b.x:  # Vertical line
            return point.x == self.a.x
        if self.a.y == self.b.y:  # Horizontal line
            return point.y == self.a.y

        # Check if point lies on the line using cross product ≈ 0
        # This is more numerically stable than checking slope equality
        cross_product = abs((point.y - self.a.y) * (self.b.x - self.a.x) -
                            (point.x - self.a.x) * (self.b.y - self.a.y))
        return cross_product < epsilon  # Use small epsilon for floating point comparison

    def contains_line(self, line: Line2D) -> bool:
        """Check if this line segment contains another line segment."""
        return self.contains_point(line.a) and self.contains_point(line.b)

    @classmethod
    def from_points_str(cls, points_str: str) -> Line2D:
        """Create a Line2D from a comma-separated string of coordinates."""
        try:
            points: List[int] = list(map(int, points_str.split(',')))
        except ValueError:
            raise ValueError(f'Invalid input: {points_str}. Ensure all values are integers.')

        if len(points) != 4:
            raise ValueError(f'Invalid line points: {points_str}. Expected 4 values.')

        return Line2D(a=Point2D(x=points[0], y=points[1]), b=Point2D(x=points[2], y=points[3]))


@dataclass(frozen=True, slots=True, kw_only=True)
class Triangle2D(Shape2D):
    """A class representing a triangle in 2D space."""
    a: Point2D
    b: Point2D
    c: Point2D
    _area: float = field(init=False, repr=False, compare=False, default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if len({self.a, self.b, self.c}) != 3:
            raise ShapeError(f'Invalid triangle points: {self.a}, {self.b}, {self.c}')

        # Pre-calculate area for better performance
        area_value = abs((self.a.x * (self.b.y - self.c.y) +
                          self.b.x * (self.c.y - self.a.y) +
                          self.c.x * (self.a.y - self.b.y))) / 2
        object.__setattr__(self, '_area', area_value)

    @property
    def area(self) -> float:
        """Return the pre-calculated area of the triangle."""
        return self._area

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is inside the triangle using the area method."""
        # Calculate areas of three sub-triangles formed with the test point
        area1 = Triangle2D(a=self.a, b=self.b, c=point).area
        area2 = Triangle2D(a=self.a, b=point, c=self.c).area
        area3 = Triangle2D(a=point, b=self.b, c=self.c).area
        # Point is inside if sum of sub-triangle areas equals triangle area
        # Use floating-point comparison with small epsilon for numerical stability
        return abs(self.area - (area1 + area2 + area3)) < epsilon

    @classmethod
    def from_points_str(cls, points_str: str) -> Triangle2D:
        """Create a Triangle2D from a comma-separated string of coordinates."""
        try:
            points: List[int] = list(map(int, points_str.split(',')))
        except ValueError:
            raise ValueError(f'Invalid input: {points_str}. Ensure all values are integers.')

        if len(points) != 6:
            raise ValueError(f'Invalid triangle points: {points_str}. Expected 6 values.')

        return Triangle2D(a=Point2D(x=points[0], y=points[1]),
                          b=Point2D(x=points[2], y=points[3]),
                          c=Point2D(x=points[4], y=points[5]))

    @classmethod
    def create_sorted(cls, a: Point2D, b: Point2D, c: Point2D) -> Triangle2D:
        """Create a Triangle2D with points sorted by polar angle."""
        if len({a, b, c}) != 3:
            raise ValueError(f'Invalid triangle points: {a}, {b}, {c}')
        a, b, c = Point2D.sort_points([a, b, c])
        return cls(a=a, b=b, c=c)

    def classify(self) -> tuple[TriangleType, TriangleType]:
        """Classify the triangle based on sides and angles.

        Returns:
            A tuple of two TriangleType enum values:
            - First value: Side-based classification (EQUILATERAL, ISOSCELES, or SCALENE)
            - Second value: Angle-based classification (RIGHT, ACUTE, or OBTUSE)
        """
        import math

        # Calculate side lengths
        sides = [Line2D(a=self.a, b=self.b).length,
                 Line2D(a=self.b, b=self.c).length,
                 Line2D(a=self.c, b=self.a).length]

        # Sort sides for easier comparison
        sides.sort()

        # Classify by sides
        if abs(sides[0] - sides[2]) < epsilon:  # All sides equal
            side_type = TriangleType.EQUILATERAL
        elif abs(sides[0] - sides[1]) < epsilon or abs(sides[1] - sides[2]) < epsilon:  # Two sides equal
            side_type = TriangleType.ISOSCELES
        else:  # No sides equal
            side_type = TriangleType.SCALENE

        # Calculate angles using the Law of Cosines
        # For a triangle with sides a, b, c, the angle C (opposite to side c) is given by:
        # cos(C) = (a² + b² - c²) / (2*a*b)
        angles = []

        # Angle opposite to side[0] (smallest side)
        cos_angle = (sides[1] ** 2 + sides[2] ** 2 - sides[0] ** 2) / (2 * sides[1] * sides[2])
        # Clamp to handle floating point errors
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angles.append(math.acos(cos_angle))

        # Angle opposite to side[1] (middle side)
        cos_angle = (sides[0] ** 2 + sides[2] ** 2 - sides[1] ** 2) / (2 * sides[0] * sides[2])
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angles.append(math.acos(cos_angle))

        # Angle opposite to side[2] (largest side)
        cos_angle = (sides[0] ** 2 + sides[1] ** 2 - sides[2] ** 2) / (2 * sides[0] * sides[1])
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angles.append(math.acos(cos_angle))

        # Classify by angles
        # Check if any angle is a right angle (π/2 radians = 90 degrees)
        if any(abs(angle - (math.pi / 2)) < epsilon for angle in angles):
            angle_type = TriangleType.RIGHT
        # Check if any angle is obtuse (> π/2 radians = 90 degrees)
        elif any(angle > (math.pi / 2 + epsilon) for angle in angles):
            angle_type = TriangleType.OBTUSE
        # Otherwise, all angles are acute (< π/2 radians = 90 degrees)
        else:
            angle_type = TriangleType.ACUTE

        return side_type, angle_type


@dataclass(frozen=True, slots=True, kw_only=True)
class Quadrilateral2D(Shape2D):
    """A class representing a quadrilateral in 2D space."""
    a: Point2D
    b: Point2D
    c: Point2D
    d: Point2D
    _area: float = field(init=False, repr=False, compare=False, default=None)  # type: ignore[assignment]
    _is_convex: bool = field(init=False, repr=False, compare=False, default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if len({self.a, self.b, self.c, self.d}) != 4:
            raise ValueError(f'Invalid quadrilateral points: {self.a}, {self.b}, {self.c}, {self.d}')

        # Pre-calculate convexity
        convexity = self._check_convexity()
        object.__setattr__(self, '_is_convex', convexity)

        # Pre-calculate area
        area_value = self._calculate_area()
        object.__setattr__(self, '_area', area_value)

    def _check_convexity(self) -> bool:
        """Check if the quadrilateral is convex."""
        # Get sorted points for consistent calculations
        a, b, c, d = Point2D.sort_points([self.a, self.b, self.c, self.d])

        # Calculate cross products between consecutive edges
        def cross(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
            return (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)

        cross_products = [cross(a, b, c), cross(b, c, d), cross(c, d, a), cross(d, a, b)]

        # Check if all cross products have the same sign (all positive or all negative)
        return all(cp >= 0 for cp in cross_products) or all(cp <= 0 for cp in cross_products)

    def _calculate_area(self) -> float:
        """Calculate the area of the quadrilateral using the shoelace formula.

        The shoelace formula works for both convex and non-convex simple quadrilaterals.
        """
        # Use the shoelace formula (Gauss's area formula) directly
        return abs((self.a.x * (self.b.y - self.d.y) +
                    self.b.x * (self.c.y - self.a.y) +
                    self.c.x * (self.d.y - self.b.y) +
                    self.d.x * (self.a.y - self.c.y))) / 2

    @property
    def area(self) -> float:
        """Return the pre-calculated area of the quadrilateral."""
        return self._area

    @property
    def is_convex(self) -> bool:
        """Return whether the quadrilateral is convex."""
        return self._is_convex

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is inside the quadrilateral.

        Uses the area comparison method for convex quadrilaterals:
        - Creates four triangles from the point and each edge
        - Compares sum of triangle areas to the quadrilateral area

        For non-convex quadrilaterals:
        - Splits the shape into two triangles
        - Checks if the point is in either triangle

        Args:
            point: The point to check

        Returns:
            True if the point is inside or on the edge of the quadrilateral
        """
        if self.is_convex:
            # For convex quadrilaterals, we can use the area method
            # Sum of areas of four triangles formed with the test point
            area1 = Triangle2D(a=self.a, b=self.b, c=point).area
            area2 = Triangle2D(a=self.b, b=self.c, c=point).area
            area3 = Triangle2D(a=self.c, b=self.d, c=point).area
            area4 = Triangle2D(a=self.d, b=self.a, c=point).area

            # Point is inside if sum of areas equals quadrilateral area
            return abs(self.area - (area1 + area2 + area3 + area4)) < epsilon
        else:
            # For non-convex quadrilaterals, split into two triangles
            triangle1 = Triangle2D(a=self.a, b=self.b, c=self.c)
            triangle2 = Triangle2D(a=self.a, b=self.c, c=self.d)
            return triangle1.contains_point(point) or triangle2.contains_point(point)

    @classmethod
    def from_points_str(cls, points_str: str) -> Quadrilateral2D:
        """Create a Quadrilateral2D from a comma-separated string of coordinates."""
        try:
            points: List[int] = list(map(int, points_str.split(',')))
        except ValueError:
            raise ValueError(f'Invalid input: {points_str}. Ensure all values are integers.')

        if len(points) != 8:
            raise ValueError(f'Invalid quadrilateral points: {points_str}. Expected 8 values.')

        return Quadrilateral2D(a=Point2D(x=points[0], y=points[1]), b=Point2D(x=points[2], y=points[3]),
                               c=Point2D(x=points[4], y=points[5]), d=Point2D(x=points[6], y=points[7]))

    def classify(self) -> QuadrilateralType:
        """Classify the quadrilateral into a specific type.

        Returns:
            A QuadrilateralType enum value that best describes this quadrilateral.
            Classification goes from most specific to most general type.
        """
        # Only classify convex quadrilaterals
        if not self.is_convex:
            return QuadrilateralType.GENERAL

        # Create the four sides as Line2D objects
        sides_as_lines = [Line2D(a=self.a, b=self.b), Line2D(a=self.b, b=self.c),
                          Line2D(a=self.c, b=self.d), Line2D(a=self.d, b=self.a)]

        # Calculate side lengths
        sides = [line.length for line in sides_as_lines]

        # Check for parallel sides
        # We'll compare slopes, handling the case of vertical lines (infinite slope)
        def are_parallel(line1: Line2D, line2: Line2D) -> bool:
            # For lines with infinite slope
            if (line1.a.x == line1.b.x) and (line2.a.x == line2.b.x):
                return True
            # For horizontal lines
            if (line1.a.y == line1.b.y) and (line2.a.y == line2.b.y):
                return True
            # General case - compare slopes
            slope1 = line1.slope()
            slope2 = line2.slope()
            if slope1 == float('inf') or slope2 == float('inf'):
                return False  # One line is vertical, the other isn't, so they can't be parallel
            return abs(slope1 - slope2) < epsilon

        # Check if opposite sides are parallel
        opposite_parallel1 = are_parallel(sides_as_lines[0], sides_as_lines[2])
        opposite_parallel2 = are_parallel(sides_as_lines[1], sides_as_lines[3])

        # Calculate angles between adjacent sides
        angles = []
        for i in range(4):
            # Get current side and next side (wrapping around)
            side1 = sides_as_lines[i]
            side2 = sides_as_lines[(i + 1) % 4]

            # Get vectors for sides
            vec1 = (side1.b.x - side1.a.x, side1.b.y - side1.a.y)
            vec2 = (side2.b.x - side2.a.x, side2.b.y - side2.a.y)

            # Calculate dot product
            dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]

            # Calculate magnitudes
            mag1 = sqrt(vec1[0] ** 2 + vec1[1] ** 2)
            mag2 = sqrt(vec2[0] ** 2 + vec2[1] ** 2)

            # Calculate angle
            cos_angle = dot_product / (mag1 * mag2)
            # Clamp to handle floating point errors
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle = acos(cos_angle)
            angles.append(angle)

        # Equal sides check (within epsilon)
        sides_equal = all(abs(sides[0] - side) < epsilon for side in sides)
        opposite_sides_equal1 = abs(sides[0] - sides[2]) < epsilon
        opposite_sides_equal2 = abs(sides[1] - sides[3]) < epsilon
        opposite_sides_equal = opposite_sides_equal1 and opposite_sides_equal2

        # Right angles check (π/2 radians = 90 degrees)
        right_angles = all(abs(angle - (pi / 2)) < epsilon for angle in angles)

        # Kite check: adjacent sides equal
        is_kite = ((abs(sides[0] - sides[1]) < epsilon and abs(sides[2] - sides[3]) < epsilon) or
                   (abs(sides[1] - sides[2]) < epsilon and abs(sides[3] - sides[0]) < epsilon))

        # Classification logic (most specific to most general)
        if sides_equal and right_angles:
            return QuadrilateralType.SQUARE
        elif right_angles:
            return QuadrilateralType.RECTANGLE
        elif sides_equal and opposite_parallel1 and opposite_parallel2:
            return QuadrilateralType.RHOMBUS
        elif opposite_parallel1 and opposite_parallel2 and opposite_sides_equal:
            return QuadrilateralType.PARALLELOGRAM
        elif opposite_parallel1 or opposite_parallel2:
            return QuadrilateralType.TRAPEZOID
        elif is_kite:
            return QuadrilateralType.KITE
        else:
            return QuadrilateralType.GENERAL


@dataclass(frozen=True, slots=True, kw_only=True)
class Polygon2D(Shape2D):
    """A class representing a polygon in 2D space."""
    vertices: tuple[Point2D, ...]
    _area: float = field(init=False, repr=False, compare=False, default=None)  # type: ignore[assignment]
    _is_convex: bool = field(init=False, repr=False, compare=False, default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        # Validate there are at least 5 unique points
        if len(self.vertices) < 5:
            raise ShapeError(f'Polygon must have at least 5 vertices, got {len(self.vertices)}')

        if len(set(self.vertices)) != len(self.vertices):
            raise ShapeError('Polygon vertices must be unique')

        # Pre-calculate convexity
        convexity = self._check_convexity()
        object.__setattr__(self, '_is_convex', convexity)

        # Pre-calculate area
        area_value = self._calculate_area()
        object.__setattr__(self, '_area', area_value)

    def _check_convexity(self) -> bool:
        """Check if the polygon is convex.

        A polygon is convex if all interior angles are less than 180 degrees.
        This can be checked by ensuring all cross products of consecutive edges have the same sign.
        """
        # Get vertices in counter-clockwise order around their centroid
        sorted_vertices = Point2D.sort_points(self.vertices)
        n = len(sorted_vertices)

        # Calculate cross products between consecutive edges
        def cross(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
            return (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)

        cross_products = []
        for i in range(n):
            p1 = sorted_vertices[i]
            p2 = sorted_vertices[(i + 1) % n]
            p3 = sorted_vertices[(i + 2) % n]
            cross_products.append(cross(p1, p2, p3))

        # Check if all cross products have the same sign (all positive or all negative)
        return all(cp >= 0 for cp in cross_products) or all(cp <= 0 for cp in cross_products)

    def _calculate_area(self) -> float:
        """Calculate the area of the polygon using the shoelace formula.

        The shoelace formula (Gauss's area formula) works for both convex and non-convex simple polygons.
        """
        n = len(self.vertices)
        area = 0.0

        # Apply shoelace formula: A = 0.5 * |∑(x_i * (y_{i+1} - y_{i-1})|
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y

        return abs(area) / 2

    @property
    def area(self) -> float:
        """Return the pre-calculated area of the polygon."""
        return self._area

    @property
    def is_convex(self) -> bool:
        """Return whether the polygon is convex."""
        return self._is_convex

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is inside the polygon.

        For convex polygons:
        - Divides the polygon into triangles from a single vertex
        - Checks if the point is in any of these triangles

        For non-convex polygons:
        - Uses ray casting algorithm (even-odd rule)

        Args:
            point: The point to check

        Returns:
            True if the point is inside or on the edge of the polygon
        """
        if self.is_convex:
            # For convex polygons, we can use the triangulation method
            # Divide polygon into triangles from the first vertex
            sorted_vertices = Point2D.sort_points(self.vertices)
            n = len(sorted_vertices)

            # Check if point is in any of the triangles
            v0 = sorted_vertices[0]  # Reference vertex
            for i in range(1, n - 1):
                triangle = Triangle2D(a=v0, b=sorted_vertices[i], c=sorted_vertices[i + 1])
                if triangle.contains_point(point):
                    return True
            return False
        else:
            # For non-convex polygons, use ray casting (even-odd rule)
            # Cast a ray from the point to the right and count intersections
            n = len(self.vertices)
            inside = False
            p1x, p1y = self.vertices[0].x, self.vertices[0].y

            for i in range(n + 1):
                p2x, p2y = self.vertices[i % n].x, self.vertices[i % n].y

                # Check if point is on an edge
                if p1y == p2y and p1y == point.y and min(p1x, p2x) < point.x < max(p1x, p2x):
                    return True

                # Check if ray from point to right crosses this edge
                if (((p1y > point.y) != (p2y > point.y)) and
                        (point.x < (p2x - p1x) * (point.y - p1y) / (p2y - p1y) + p1x)):
                    inside = not inside

                p1x, p1y = p2x, p2y

            return inside

    def is_regular(self) -> bool:
        """Check if the polygon is regular (all sides and angles equal).

        A regular polygon has all sides equal in length and all interior angles equal.
        """
        return self.classify() == PolygonType.REGULAR

    def classify(self) -> PolygonType:
        """Classify the polygon based on its sides and angles properties.

        Classification is based on the following criteria:
        - REGULAR: Convex polygon with all sides equal and all angles equal
        - EQUILATERAL: Convex polygon with all sides equal but angles may differ
        - EQUIANGULAR: Convex polygon with all angles equal but sides may differ
        - CONVEX: Polygon with all interior angles less than 180 degrees
        - CONCAVE: Polygon with at least one interior angle greater than 180 degrees
        - GENERAL: Fallback classification if none of the above apply

        Returns:
            The most specific PolygonType that describes this polygon
        """
        n = len(self.vertices)

        # Check convexity first
        if not self.is_convex:
            return PolygonType.CONCAVE

        # Get vertices in counter-clockwise order
        sorted_vertices = Point2D.sort_points(self.vertices)

        # Calculate all side lengths
        sides = []
        for i in range(n):
            p1 = sorted_vertices[i]
            p2 = sorted_vertices[(i + 1) % n]
            sides.append(Line2D(a=p1, b=p2).length)

        # Calculate all interior angles
        angles = []
        for i in range(n):
            p_prev = sorted_vertices[(i - 1) % n]
            p_curr = sorted_vertices[i]
            p_next = sorted_vertices[(i + 1) % n]

            # Create vectors
            v1x, v1y = p_curr.x - p_prev.x, p_curr.y - p_prev.y
            v2x, v2y = p_next.x - p_curr.x, p_next.y - p_curr.y

            # Calculate dot product and magnitudes
            dot_product = v1x * v2x + v1y * v2y
            mag1 = sqrt(v1x ** 2 + v1y ** 2)
            mag2 = sqrt(v2x ** 2 + v2y ** 2)

            # Calculate angle in radians
            cosine = dot_product / (mag1 * mag2)
            # Clamp to handle floating point errors
            cosine = max(-1.0, min(1.0, cosine))
            # Calculate interior angle (π - exterior angle)
            angles.append(pi - acos(cosine))

        # Check if all sides are equal length
        sides_equal = all(abs(sides[0] - side) < epsilon for side in sides)

        # Check if all angles are equal
        angles_equal = all(abs(angles[0] - angle) < epsilon for angle in angles)

        # Determine polygon type
        if sides_equal and angles_equal:
            return PolygonType.REGULAR
        elif sides_equal:
            return PolygonType.EQUILATERAL
        elif angles_equal:
            return PolygonType.EQUIANGULAR
        else:
            return PolygonType.CONVEX
