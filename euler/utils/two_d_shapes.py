#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two-dimensional geometric shapes module.

This module provides classes and functions for working with 2D geometric shapes such as
points, line segments, polygons, and related operations. It supports basic geometric calculations like
point containment checks, shape classification, and polygon creation from string input.

Classes:
    Point2D: Represents an immutable point in 2D space with x and y coordinates.
    LineSegment2D: Represents an immutable line segment defined by two endpoints.
    Polygon2D: Represents an immutable polygon defined by a tuple of vertices.
    ShapeError: Exception raised for invalid shape operations or creation.

Functions:
    from_points_str: Creates a Polygon2D from a comma-separated string of coordinates.

Constants:
    epsilon: A small float value used for floating-point comparisons.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import ClassVar, Dict, List, Tuple

from euler.types import EulerError

epsilon: float = 1e-10


def from_points_str(comma_seperated_points_str: str) -> Polygon2D:
    """Create a Polygon2D from a comma-separated string of coordinates.

    The input string should contain an even number of numerical values that represent
    the x and y coordinates of the polygon vertices in sequence.

    Args:
        comma_seperated_points_str: A string of comma-separated numbers (e.g., "0,0,1,0,1,1,0,1")

    Returns:
        A Polygon2D instance with vertices created from the input coordinates

    Raises:
        ShapeError: If the input is invalid (not numbers, odd number of values, or fewer than 2 values)
    """
    try:
        points: List[float] = list(map(float, comma_seperated_points_str.split(',')))
    except ValueError:
        raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Ensure all values are floats or integers.')
    else:
        if (len_points := len(points)) < 2:
            raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Expected at least two values.')
        if len_points % 2 != 0:
            raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Expected an even number of values.')
    return Polygon2D(vertices=tuple(Point2D(x=points[i], y=points[i + 1]) for i in range(0, len(points), 2)))


class ShapeError(EulerError):
    """Exception raised for errors in geometric shape validation or creation.

    This exception is raised when attempting to create invalid geometric shapes,
    such as a triangle with two points, a line with coincident points,
    or a non-simple quadrilateral.
    """
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class Point2D:
    """A class representing a point in 2D space.

    This immutable class represents a point with x and y coordinates in a 2D space.
    Supports vector operations such as addition, subtraction, and cross product.

    Attributes:
        x: The x-coordinate of the point
        y: The y-coordinate of the point
    """
    x: float
    y: float

    def __eq__(self, other: object) -> bool:
        """Check if two points are equal."""
        if not isinstance(other, Point2D):
            return False
        return isclose(self.x, other.x, abs_tol=epsilon) and isclose(self.y, other.y, abs_tol=epsilon)

    def __add__(self, other: Point2D) -> Point2D:
        """Add two points as vectors.

        Args:
            other: The point to add to this point

        Returns:
            A new Point2D with coordinates that are the sum of this point and the other point
        """
        return Point2D(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        """Subtract a point from this point as vectors.

        Args:
            other: The point to subtract from this point

        Returns:
            A new Point2D with coordinates that are the difference of this point and the other point
        """
        return Point2D(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: Point2D) -> float:
        """Calculate the cross product of two points as vectors.

        The cross product is calculated as (self.x * other.y - self.y * other.x).
        This is useful for determining relative orientation of vectors and checking collinearity.

        Args:
            other: The point to multiply with this point

        Returns:
            The cross product of the two points as vectors
        """
        return self.x * other.y - self.y * other.x


@dataclass(frozen=True, slots=True, kw_only=True)
class LineSegment2D:
    """A class representing a line segment in 2D space.

    This immutable class represents a line segment defined by two endpoints.
    It provides methods for checking if a point lies on the line segment.

    Attributes:
        a: The first endpoint of the line segment
        b: The second endpoint of the line segment
    """
    a: Point2D
    b: Point2D

    def point_on_segment(self, point: Point2D) -> bool:
        """Check if the point is on the line segment.

        This method first checks if the point equals either endpoint for efficiency.
        Then it checks if the point is within the bounding box of the line segment.
        Finally, it uses the cross product to determine if the point is collinear with the line segment.

        Args:
            point: The point to check

        Returns:
            True if the point lies on the line segment, False otherwise
        """
        if point == self.a or point == self.b:
            return True
        lower_bound_x, upper_bound_x = sorted([self.a.x, self.b.x])
        lower_bound_y, upper_bound_y = sorted([self.a.y, self.b.y])
        if lower_bound_x <= point.x <= upper_bound_x and lower_bound_y <= point.y <= upper_bound_y:
            # Calculate the cross product of vectors (b-a) and (point-a),
            # If cross product is 0, point is collinear with line segment
            return isclose((self.b - self.a) * (point - self.a), 0.0, abs_tol=epsilon)
        return False


@dataclass(frozen=True, slots=True, kw_only=True)
class Polygon2D:
    """A class representing a polygon in 2D space.

    This immutable class represents a polygon defined by an ordered tuple of vertices.
    It supports basic geometric operations like point containment checks and shape classification.
    The polygon can have any number of sides, including degenerate cases like points and lines.

    Attributes:
        vertices: A tuple of Point2D objects representing the polygon vertices in order
        shape_names: A class variable mapping the number of sides to shape names
    """
    shape_names: ClassVar[Dict[int, str]] = {1: 'point', 2: 'line', 3: 'triangle', 4: 'quadrilateral', 5: 'pentagon',
                                             6: 'hexagon', 7: 'heptagon', 8: 'octagon', 9: 'nonagon', 10: 'decagon'}
    vertices: Tuple[Point2D, ...]

    def __post_init__(self) -> None:
        """Initialize and validate the polygon after instance creation.

        This method validates that the polygon has at least one vertex.

        Raises:
            ShapeError: If no vertices are provided
        """
        if len(self.vertices) == 0:
            raise ShapeError('Polygon must have at least one vertex, none given.')

    def contains_point(self, point: Point2D) -> bool:
        """Check if the polygon contains the given point.

        Uses the ray casting algorithm (also known as the even-odd rule or crossing number algorithm)
        to determine if a point is inside a polygon. This method casts a ray from the test point
        in any fixed direction and counts the number of times it intersects with the polygon's edges.
        If the number of intersections is odd, the point is inside; if even, it's outside.

        This method works for both convex and concave polygons, as well as self-intersecting ones.
        Points exactly on an edge (horizontal, vertical, or inclined) or vertex are considered inside the polygon.

        For degenerate cases (points and lines), a point is contained only if it equals one of the vertices
        or lies on the line segment between vertices.

        Args:
            point: The Point2D to check for containment

        Returns:
            True if the point is inside or on the boundary of the polygon, False otherwise
        """
        # Handle special cases: point, line
        num_sides: int = len(self.vertices)
        if num_sides == 1:
            # For a point, check if the point is equal to the vertex
            return point == self.vertices[0]
        if num_sides == 2:
            # For a line, use the LineSegment2D class to check if point is on the line
            line_segment = LineSegment2D(a=self.vertices[0], b=self.vertices[1])
            return line_segment.point_on_segment(point)

        # Check if point is on any vertex
        if any(vertex == point for vertex in self.vertices):
            return True

        # Ray casting algorithm (even-odd rule)
        # Cast a ray from point to the right (positive x direction) and count intersections with polygon edges
        # If the number of intersections is odd, the point is inside; if even, it's outside
        inside: bool = False
        x, y = point.x, point.y

        # Loop through all edges of the polygon
        for edge in (LineSegment2D(a=self.vertices[i], b=self.vertices[(i + 1) % num_sides]) for i in range(num_sides)):
            # If point is on this edge, it's inside
            if edge.point_on_segment(point):
                return True

            # Get edge endpoints coordinates
            vax, vay, vbx, vby = edge.a.x, edge.a.y, edge.b.x, edge.b.y

            # Ray-casting intersection check:
            # 1. Check if the ray crosses the edge (y is between the y-coordinates of the endpoints)
            # 2. Calculate the x-coordinate of the intersection and check if it's to the right of the point
            if ((vay > y) != (vby > y)) and (x < vax + (y - vay) * (vbx - vax) / (vby - vay)):
                inside = not inside

        return inside

    @property
    def shape(self) -> str:
        """Return the name of the polygon based on its number of sides.

        Common shapes (up to decagon) have specific names from the shape_names dictionary.
        Shapes with more than 10 sides are simply called 'polygon'.

        Returns:
            A string representing the name of the shape
        """
        return self.__class__.shape_names.get(len(self.vertices), 'polygon')
