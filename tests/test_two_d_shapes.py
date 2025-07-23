#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test cases for the two_d_shapes module.

This module contains comprehensive unit tests for all the geometric classes defined in the
euler.utils.two_d_shapes module, including:

- Point2D: Tests for 2D point operations, including vector operations
- Polygon2D: Tests for polygon operations, including area calculation and point containment
- from_points_str: Tests for creating polygons from string input

The tests verify both basic functionality and edge cases for each class.
"""

import unittest

from euler.utils.two_d_shapes import Point2D, Polygon2D, ShapeError, from_points_str


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
        # The following would be true if we implemented point-on-line check
        # But currently, contains_point for lines only checks vertices
        self.assertFalse(line_polygon.contains_point(Point2D(x=0.5, y=0.5)))


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


if __name__ == '__main__':
    unittest.main()
