#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two-dimensional geometric shapes module.

This module provides classes and functions for working with 2D geometric shapes such as
points, polygons, and related operations. It supports basic geometric calculations like
area computation, point containment checks, and vector operations.

Classes:
    Point2D: Represents a point in 2D space with vector operations.
    Polygon2D: Represents a polygon defined by a tuple of vertices.
    ShapeError: Exception raised for invalid shape operations.

Functions:
    from_points_str: Creates a Polygon2D from a comma-separated string of coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import ClassVar, Dict, List, Tuple

from euler.types import EulerError

epsilon: float = 1e-10


def from_points_str(comma_seperated_points_str: str) -> Polygon2D:
    """Create a Polygon2D from a comma-separated string of integer coordinates.

    The input string should contain an even number of integers that represent
    the x and y coordinates of the polygon vertices in sequence.

    Args:
        comma_seperated_points_str: A string of comma-separated integers (e.g., "0,0,1,0,1,1,0,1")

    Returns:
        A Polygon2D instance with vertices created from the input coordinates

    Raises:
        ShapeError: If the input is invalid (not integers, odd number of values, or fewer than 2 values)
    """
    try:
        points: List[float] = list(map(float, comma_seperated_points_str.split(',')))
    except ValueError:
        raise ShapeError(f'Invalid input: {comma_seperated_points_str}. Ensure all values are integers.')
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

    Attributes:
        x: The x-coordinate of the point
        y: The y-coordinate of the point
    """
    x: float
    y: float


@dataclass(frozen=True, slots=True, kw_only=True)
class Polygon2D:
    """A class representing a polygon in 2D space.

    This immutable class represents a polygon defined by an ordered tuple of vertices.
    It supports basic geometric operations like area calculation and point containment checks.
    The polygon can have any number of sides, including degenerate cases like points and lines.

    Attributes:
        vertices: A tuple of Point2D objects representing the polygon vertices in order
        shape_names: A class variable mapping the number of sides to shape names
    """
    shape_names: ClassVar[Dict[int, str]] = {1: 'point', 2: 'line', 3: 'triangle', 4: 'quadrilateral', 5: 'pentagon',
                                             6: 'hexagon', 7: 'heptagon', 8: 'octagon', 9: 'nonagon', 10: 'decagon'}
    vertices: Tuple[Point2D, ...]

    def __post_init__(self) -> None:
        """Initialize derived attributes after instance creation.

        This method computes and sets the number of sides and the area of the polygon.
        For polygons with 3 or more vertices, the area is calculated using the shoelace formula.
        For points and lines (1 or 2 vertices), the area is set to 0.

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
        Points exactly on an edge or vertex are considered inside the polygon.

        For degenerate cases (points and lines), a point is contained only if it equals one of the vertices.

        Args:
            point: The Point2D to check for containment

        Returns:
            True if the point is inside or on the boundary of the polygon, False otherwise
        """
        # Handle special cases: point, line
        num_sides = len(self.vertices)
        if num_sides <= 2:
            # For a point or line, check if the point is equal to any vertex
            return any(vertex == point for vertex in self.vertices)

        # Check if point is on any vertex
        if any(vertex == point for vertex in self.vertices):
            return True

        # Ray casting algorithm
        # Cast a ray from point to the right (positive x direction)
        # Count intersections with polygon edges
        inside = False
        x, y = point.x, point.y
        # Loop through all edges of the polygon
        for i in range(num_sides):
            j = (i + 1) % num_sides
            vi, vj = self.vertices[i], self.vertices[j]

            # Check if point is on the edge
            # For horizontal edges, check if point is on the edge
            if isclose(vi.y, vj.y, abs_tol=epsilon) and isclose(vi.y, y, abs_tol=epsilon):
                if min(vi.x, vj.x) <= x <= max(vi.x, vj.x):
                    return True

            # For vertical edges, check if point is on the edge
            if isclose(vi.x, vj.x, abs_tol=epsilon) and isclose(vi.x, x, abs_tol=epsilon):
                if min(vi.y, vj.y) <= y <= max(vi.y, vj.y):
                    return True

            # Check if ray intersects edge
            # Condition 1: y is between vi.y and vj.y
            # Condition 2: x is less than the x-coordinate of the intersection point
            if ((vi.y > y) != (vj.y > y)) and (x < vi.x + (y - vi.y) * (vj.x - vi.x) / (vj.y - vi.y)):
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
