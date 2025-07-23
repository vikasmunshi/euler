#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test cases for the two_d_shapes module.

This module contains comprehensive unit tests for all the geometric classes defined in the
euler.utils.two_d_shapes module, including:

- Point2D: Tests for 2D point operations, including vector operations
- LineSegment2D: Tests for line segment operations, including point-on-segment checks
- Polygon2D: Tests for polygon operations, including point containment
- from_points_str: Tests for creating polygons from string input

The tests verify both basic functionality and edge cases for each class.
"""

import unittest

from euler.utils.two_d_shapes import LineSegment2D, Point2D, Polygon2D, ShapeError, from_points_str


class TestPoint2D(unittest.TestCase):
    """Test cases for the Point2D class."""

    def test_initialization(self):
        """Test point initialization and attribute access."""
        point = Point2D(x=1.0, y=2.0)
        self.assertEqual(1.0, point.x)
        self.assertEqual(2.0, point.y)

    def test_equality(self):
        """Test equality comparison between points."""
        point1 = Point2D(x=1.0, y=2.0)
        point2 = Point2D(x=1.0, y=2.0)
        point3 = Point2D(x=3.0, y=4.0)

        self.assertEqual(point1, point2)
        self.assertNotEqual(point1, point3)

    def test_vector_operations(self):
        """Test vector operations on points."""
        p1 = Point2D(x=1.0, y=2.0)
        p2 = Point2D(x=3.0, y=4.0)

        # Test addition
        result = p1 + p2
        self.assertEqual(result.x, 4.0)
        self.assertEqual(result.y, 6.0)

        # Test subtraction
        result = p2 - p1
        self.assertEqual(result.x, 2.0)
        self.assertEqual(result.y, 2.0)

        # Test cross product
        # Cross product of (1,2) and (3,4) is 1*4 - 2*3 = 4 - 6 = -2
        result = p1 * p2
        self.assertEqual(result, -2.0)


class TestLineSegment2D(unittest.TestCase):
    """Test cases for the LineSegment2D class."""

    def test_initialization(self):
        """Test line segment initialization."""
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=1.0, y=1.0)
        segment = LineSegment2D(a=p1, b=p2)

        self.assertEqual(segment.a, p1)
        self.assertEqual(segment.b, p2)

    def test_point_on_segment(self):
        """Test point_on_segment method."""
        segment = LineSegment2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=2.0, y=2.0))

        # Points on the segment
        self.assertTrue(segment.point_on_segment(Point2D(x=0.0, y=0.0)))  # Endpoint a
        self.assertTrue(segment.point_on_segment(Point2D(x=2.0, y=2.0)))  # Endpoint b
        self.assertTrue(segment.point_on_segment(Point2D(x=1.0, y=1.0)))  # Middle point
        self.assertTrue(segment.point_on_segment(Point2D(x=0.5, y=0.5)))  # Another point on segment

        # Points not on the segment
        self.assertFalse(segment.point_on_segment(Point2D(x=3.0, y=3.0)))  # Beyond segment
        self.assertFalse(segment.point_on_segment(Point2D(x=-1.0, y=-1.0)))  # Before segment
        self.assertFalse(segment.point_on_segment(Point2D(x=1.0, y=0.0)))  # Off the line

        # Horizontal segment
        horizontal = LineSegment2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=2.0, y=0.0))
        self.assertTrue(horizontal.point_on_segment(Point2D(x=1.0, y=0.0)))
        self.assertFalse(horizontal.point_on_segment(Point2D(x=1.0, y=0.1)))

        # Vertical segment
        vertical = LineSegment2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=0.0, y=2.0))
        self.assertTrue(vertical.point_on_segment(Point2D(x=0.0, y=1.0)))
        self.assertFalse(vertical.point_on_segment(Point2D(x=0.1, y=1.0)))


class TestPolygon2D(unittest.TestCase):
    """Test cases for the Polygon2D class."""

    def test_initialization(self):
        """Test polygon initialization and basic properties."""
        # Triangle
        triangle_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=0.0, y=1.0)
        )
        triangle = Polygon2D(vertices=triangle_vertices)

        self.assertEqual(triangle_vertices, triangle.vertices)
        self.assertEqual('triangle', triangle.shape)

        # Quadrilateral
        quad_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=1.0, y=1.0),
            Point2D(x=0.0, y=1.0)
        )
        quad = Polygon2D(vertices=quad_vertices)

        self.assertEqual(quad_vertices, quad.vertices)
        self.assertEqual('quadrilateral', quad.shape)

        # Pentagon
        pentagon_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=1.5, y=0.5),
            Point2D(x=1.0, y=1.0),
            Point2D(x=0.0, y=1.0)
        )
        pentagon = Polygon2D(vertices=pentagon_vertices)

        self.assertEqual(pentagon_vertices, pentagon.vertices)
        self.assertEqual('pentagon', pentagon.shape)

    def test_degenerate_cases(self):
        """Test degenerate cases like points and lines."""
        # Point
        point_vertices = (Point2D(x=1.0, y=1.0),)
        point_polygon = Polygon2D(vertices=point_vertices)

        self.assertEqual('point', point_polygon.shape)

        # Line
        line_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=1.0)
        )
        line_polygon = Polygon2D(vertices=line_vertices)

        self.assertEqual('line', line_polygon.shape)

    def test_empty_polygon_error(self):
        """Test that creating a polygon with no vertices raises an error."""
        with self.assertRaises(ShapeError):
            Polygon2D(vertices=())

    def test_point_containment_triangles(self):
        """Test point containment for triangles."""
        triangle_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=2.0, y=0.0),
            Point2D(x=0.0, y=2.0)
        )
        triangle = Polygon2D(vertices=triangle_vertices)

        # Points on inclined edge
        self.assertTrue(triangle.contains_point(Point2D(x=0.0, y=1.0)))  # Vertical edge
        self.assertTrue(triangle.contains_point(Point2D(x=1.0, y=0.0)))  # Horizontal edge
        # Point on inclined edge from (0,2) to (2,0)
        self.assertTrue(triangle.contains_point(Point2D(x=1.0, y=1.0)))  # Inclined edge

        # Points inside
        self.assertTrue(triangle.contains_point(Point2D(x=0.5, y=0.5)))
        self.assertTrue(triangle.contains_point(Point2D(x=0.1, y=0.1)))

        # Points on edges
        self.assertTrue(triangle.contains_point(Point2D(x=1.0, y=0.0)))  # Edge
        self.assertTrue(triangle.contains_point(Point2D(x=0.0, y=1.0)))  # Edge
        self.assertTrue(triangle.contains_point(Point2D(x=0.0, y=0.0)))  # Vertex

        # Points outside
        self.assertFalse(triangle.contains_point(Point2D(x=1.0, y=1.5)))
        self.assertFalse(triangle.contains_point(Point2D(x=2.0, y=2.0)))
        self.assertFalse(triangle.contains_point(Point2D(x=-0.1, y=-0.1)))

    def test_point_containment_quadrilaterals(self):
        """Test point containment for quadrilaterals."""
        square_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=1.0, y=1.0),
            Point2D(x=0.0, y=1.0)
        )
        square = Polygon2D(vertices=square_vertices)

        # Points inside
        self.assertTrue(square.contains_point(Point2D(x=0.5, y=0.5)))
        self.assertTrue(square.contains_point(Point2D(x=0.25, y=0.75)))

        # Points on edges
        self.assertTrue(square.contains_point(Point2D(x=0.5, y=0.0)))  # Edge
        self.assertTrue(square.contains_point(Point2D(x=1.0, y=0.5)))  # Edge
        self.assertTrue(square.contains_point(Point2D(x=0.0, y=0.0)))  # Vertex

        # Points outside
        self.assertFalse(square.contains_point(Point2D(x=1.5, y=1.5)))
        self.assertFalse(square.contains_point(Point2D(x=-0.1, y=0.5)))

    def test_point_containment_complex_polygons(self):
        """Test point containment for more complex polygons."""
        # Concave polygon
        concave_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=4.0, y=0.0),
            Point2D(x=4.0, y=4.0),
            Point2D(x=2.0, y=2.0),  # This creates a concavity
            Point2D(x=0.0, y=4.0)
        )
        concave = Polygon2D(vertices=concave_vertices)

        # Points inside convex region
        self.assertTrue(concave.contains_point(Point2D(x=1.0, y=1.0)))
        self.assertTrue(concave.contains_point(Point2D(x=3.0, y=1.0)))

        # Points in the concave region (should be inside)
        self.assertTrue(concave.contains_point(Point2D(x=2.5, y=2.5)))

        # Points outside
        self.assertFalse(concave.contains_point(Point2D(x=5.0, y=2.0)))
        self.assertFalse(concave.contains_point(Point2D(x=-1.0, y=-1.0)))

    def test_point_containment_degenerate_cases(self):
        """Test point containment for degenerate cases (point, line)."""
        # Point
        point_vertices = (Point2D(x=1.0, y=1.0),)
        point_polygon = Polygon2D(vertices=point_vertices)

        self.assertTrue(point_polygon.contains_point(Point2D(x=1.0, y=1.0)))  # Same point
        self.assertFalse(point_polygon.contains_point(Point2D(x=1.1, y=1.0)))  # Different point

        # Line
        line_vertices = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=1.0)
        )
        line_polygon = Polygon2D(vertices=line_vertices)

        self.assertTrue(line_polygon.contains_point(Point2D(x=0.0, y=0.0)))  # Endpoint
        self.assertTrue(line_polygon.contains_point(Point2D(x=1.0, y=1.0)))  # Endpoint
        self.assertFalse(line_polygon.contains_point(Point2D(x=0.5, y=0.6)))  # Off the line
        self.assertFalse(line_polygon.contains_point(Point2D(x=2, y=2)))  # On the line, outside the segment
        self.assertFalse(line_polygon.contains_point(Point2D(x=-2, y=-2)))  # On the line, outside the segment
        # Check that points on the line segment are properly detected
        self.assertTrue(line_polygon.contains_point(Point2D(x=0.5, y=0.5)))  # On the line
        self.assertTrue(line_polygon.contains_point(Point2D(x=0.25, y=0.25)))  # On the line


class TestFromPointsStr(unittest.TestCase):
    """Test cases for the from_points_str function."""

    def test_valid_input(self):
        """Test from_points_str with valid input."""
        # Square
        square_str = "0,0,1,0,1,1,0,1"
        square = from_points_str(square_str)

        self.assertEqual('quadrilateral', square.shape)

        # Triangle
        triangle_str = "0,0,1,0,0,1"
        triangle = from_points_str(triangle_str)

        self.assertEqual('triangle', triangle.shape)

    def test_invalid_input(self):
        """Test from_points_str with invalid input."""
        # Non-numeric values
        with self.assertRaises(ShapeError):
            from_points_str("a,b,c,d")

        # Odd number of values
        with self.assertRaises(ShapeError):
            from_points_str("0,0,1,0,1")

        # Too few values
        with self.assertRaises(ShapeError):
            from_points_str("0")


class TestEdgeCases(unittest.TestCase):
    """Test special edge cases in geometric calculations."""

    def test_point_on_inclined_edge(self):
        """Test specific case of points on inclined edges."""
        # Create a polygon with an inclined edge
        polygon = Polygon2D(vertices=(
            Point2D(x=0.0, y=0.0),
            Point2D(x=2.0, y=0.0),
            Point2D(x=2.0, y=2.0),
            Point2D(x=0.0, y=2.0)
        ))

        # Create a point on an inclined edge (if we added a diagonal)
        diagonal_point = Point2D(x=1.0, y=1.0)

        # This point is inside the square but not on any edge
        self.assertTrue(polygon.contains_point(diagonal_point))
        self.assertTrue(polygon.contains_point(Point2D(x=1.5, y=0.5)))

        # Create a triangle with an inclined edge
        triangle = Polygon2D(vertices=(
            Point2D(x=0.0, y=0.0),
            Point2D(x=2.0, y=0.0),
            Point2D(x=1.0, y=2.0)
        ))

        # Point on the inclined edge from (2,0) to (1,2)
        inclined_point = Point2D(x=1.5, y=1.0)
        self.assertTrue(triangle.contains_point(inclined_point))

        # Very precise edge case - point exactly on a nearly vertical line
        nearly_vertical = Polygon2D(vertices=(
            Point2D(x=0.0, y=0.0),
            Point2D(x=0.001, y=2.0),
            Point2D(x=2.0, y=0.0)
        ))

        self.assertTrue(nearly_vertical.contains_point(Point2D(x=0.0005, y=1.0)))


if __name__ == '__main__':
    unittest.main()
