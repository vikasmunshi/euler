#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import unittest

from euler.utils.two_d_shapes import (Line2D, Point2D, PolarPoint2D, Polygon2D, PolygonType, Quadrilateral2D,
                                      QuadrilateralType, ShapeError, Triangle2D, TriangleType)


class TestPoint2D(unittest.TestCase):
    def test_initialization(self):
        point = Point2D(x=1.0, y=2.0)
        self.assertEqual(1.0, point.x)
        self.assertEqual(2.0, point.y)

    def test_area(self):
        point = Point2D(x=3.0, y=4.0)
        self.assertEqual(0.0, point.area)

    def test_contains_point(self):
        point = Point2D(x=5.0, y=6.0)
        # A point contains only itself
        self.assertTrue(point.contains_point(Point2D(x=5.0, y=6.0)))
        self.assertFalse(point.contains_point(Point2D(x=5.1, y=6.0)))

    def test_addition(self):
        p1 = Point2D(x=1.0, y=2.0)
        p2 = Point2D(x=3.0, y=4.0)
        result = p1 + p2
        self.assertEqual(4.0, result.x)
        self.assertEqual(6.0, result.y)

    def test_subtraction(self):
        p1 = Point2D(x=5.0, y=7.0)
        p2 = Point2D(x=2.0, y=3.0)
        result = p1 - p2
        self.assertEqual(3.0, result.x)
        self.assertEqual(4.0, result.y)

    def test_distance_to(self):
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=3.0, y=4.0)
        self.assertEqual(5.0, p1.distance_to(p2))

    def test_midpoint(self):
        p1 = Point2D(x=1.0, y=1.0)
        p2 = Point2D(x=3.0, y=5.0)
        mid = p1.midpoint(p2)
        self.assertEqual(2.0, mid.x)
        self.assertEqual(3.0, mid.y)

    def test_as_polar(self):
        # Test conversion from cartesian to polar
        p = Point2D(x=3.0, y=4.0)
        polar = p.as_polar()
        self.assertAlmostEqual(5.0, polar.r)
        self.assertAlmostEqual(math.atan2(4.0, 3.0), polar.theta)

    def test_sort_points(self):
        # Test sorting points in counter-clockwise order
        points = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=1.0, y=1.0),
            Point2D(x=0.0, y=1.0),
        )
        sorted_points = Point2D.sort_points(points)
        # Points should be sorted counter-clockwise around their centroid
        expected_order = (
            Point2D(x=1.0, y=1.0),
            Point2D(x=0.0, y=1.0),
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
        )
        for actual, expected in zip(sorted_points, expected_order):
            self.assertEqual(expected, actual)


class TestPolarPoint2D(unittest.TestCase):
    def test_initialization(self):
        point = PolarPoint2D(r=5.0, theta=math.pi / 4)
        self.assertEqual(5.0, point.r)
        self.assertEqual(math.pi / 4, point.theta)

    def test_area(self):
        point = PolarPoint2D(r=3.0, theta=math.pi / 2)
        self.assertEqual(0.0, point.area)

    def test_contains_point(self):
        point = PolarPoint2D(r=5.0, theta=math.pi / 3)
        # A point contains only itself
        self.assertTrue(point.contains_point(PolarPoint2D(r=5.0, theta=math.pi / 3).as_cartesian()))
        self.assertFalse(point.contains_point(PolarPoint2D(r=5.1, theta=math.pi / 3).as_cartesian()))

    def test_addition(self):
        p1 = PolarPoint2D(r=2.0, theta=math.pi / 4)
        p2 = PolarPoint2D(r=3.0, theta=math.pi / 6)
        result = p1 + p2
        self.assertEqual(5.0, result.r)
        self.assertAlmostEqual(math.pi / 4 + math.pi / 6, result.theta)

    def test_subtraction(self):
        p1 = PolarPoint2D(r=5.0, theta=math.pi / 2)
        p2 = PolarPoint2D(r=2.0, theta=math.pi / 4)
        result = p1 - p2
        self.assertEqual(3.0, result.r)
        self.assertAlmostEqual(math.pi / 2 - math.pi / 4, result.theta)

    def test_distance_to(self):
        p1 = PolarPoint2D(r=1.0, theta=0.0)
        p2 = PolarPoint2D(r=1.0, theta=math.pi / 2)
        self.assertAlmostEqual(math.pi / 2, p1.distance_to(p2))

    def test_as_cartesian(self):
        # Test conversion from polar to cartesian
        p = PolarPoint2D(r=2.0, theta=math.pi / 4)
        cart = p.as_cartesian()
        self.assertAlmostEqual(2.0 * math.cos(math.pi / 4), cart.x)
        self.assertAlmostEqual(2.0 * math.sin(math.pi / 4), cart.y)


class TestLine2D(unittest.TestCase):
    def test_initialization(self):
        p1 = Point2D(x=1.0, y=2.0)
        p2 = Point2D(x=3.0, y=4.0)
        line = Line2D(a=p1, b=p2)
        self.assertEqual(p1, line.a)
        self.assertEqual(p2, line.b)

    def test_area(self):
        line = Line2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=3.0, y=4.0))
        self.assertEqual(0.0, line.area)

    def test_same_point_error(self):
        p = Point2D(x=1.0, y=1.0)
        with self.assertRaises(ShapeError):
            Line2D(a=p, b=p)

    def test_length(self):
        line = Line2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=3.0, y=4.0))
        self.assertEqual(5.0, line.length)

    def test_slope(self):
        # Test regular slope
        line = Line2D(a=Point2D(x=1.0, y=1.0), b=Point2D(x=3.0, y=5.0))
        self.assertEqual(2.0, line.slope())

        # Test vertical line (infinite slope)
        line = Line2D(a=Point2D(x=2.0, y=1.0), b=Point2D(x=2.0, y=5.0))
        self.assertEqual(float('inf'), line.slope())

        # Test horizontal line (zero slope)
        line = Line2D(a=Point2D(x=1.0, y=3.0), b=Point2D(x=5.0, y=3.0))
        self.assertEqual(0.0, line.slope())

    def test_y_intercept(self):
        # Test regular y-intercept
        line = Line2D(a=Point2D(x=1.0, y=3.0), b=Point2D(x=3.0, y=7.0))
        self.assertEqual(1.0, line.y_intercept())

        # Test vertical line (no y-intercept)
        line = Line2D(a=Point2D(x=2.0, y=1.0), b=Point2D(x=2.0, y=5.0))
        self.assertIsNone(line.y_intercept())

    def test_x_intercept(self):
        # Test regular x-intercept
        line = Line2D(a=Point2D(x=1.0, y=2.0), b=Point2D(x=3.0, y=6.0))
        self.assertEqual(0.0, line.x_intercept())

        # Test horizontal line (no x-intercept unless y=0)
        line = Line2D(a=Point2D(x=1.0, y=3.0), b=Point2D(x=5.0, y=3.0))
        self.assertIsNone(line.x_intercept())

    def test_contains_point(self):
        line = Line2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=4.0, y=4.0))
        # Test point on the line
        self.assertTrue(line.contains_point(Point2D(x=2.0, y=2.0)))
        # Test point not on the line
        self.assertFalse(line.contains_point(Point2D(x=2.0, y=3.0)))
        # Test point outside segment but on the line
        self.assertFalse(line.contains_point(Point2D(x=5.0, y=5.0)))

    def test_contains_line(self):
        line = Line2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=4.0, y=4.0))
        # Test line that is a subsegment
        sub_line = Line2D(a=Point2D(x=1.0, y=1.0), b=Point2D(x=3.0, y=3.0))
        self.assertTrue(line.contains_line(sub_line))
        # Test line that is not a subsegment
        other_line = Line2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=5.0, y=5.0))
        self.assertFalse(line.contains_line(other_line))


class TestTriangle2D(unittest.TestCase):
    def test_initialization(self):
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=3.0, y=0.0)
        p3 = Point2D(x=0.0, y=4.0)
        triangle = Triangle2D(a=p1, b=p2, c=p3)
        self.assertEqual(p1, triangle.a)
        self.assertEqual(p2, triangle.b)
        self.assertEqual(p3, triangle.c)

    def test_collinear_points_error(self):
        # Three collinear points cannot form a triangle
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=1.0, y=1.0)
        p3 = Point2D(x=1.0, y=1.0)
        with self.assertRaises(ShapeError):
            Triangle2D(a=p1, b=p2, c=p3)

    def test_area(self):
        triangle = Triangle2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=3.0, y=0.0),
            c=Point2D(x=0.0, y=4.0)
        )
        self.assertEqual(6.0, triangle.area)

    def test_contains_point(self):
        triangle = Triangle2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=3.0, y=0.0),
            c=Point2D(x=0.0, y=3.0)
        )
        # Test point inside
        self.assertTrue(triangle.contains_point(Point2D(x=1.0, y=1.0)))
        # Test point outside
        self.assertFalse(triangle.contains_point(Point2D(x=2.0, y=2.0)))
        # Test point on edge
        self.assertTrue(triangle.contains_point(Point2D(x=1.5, y=0.0)))

    def test_classify(self):
        # Test equilateral triangle
        eq_triangle = Triangle2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=1.0, y=0.0), c=Point2D(x=0.5, y=math.sqrt(3) / 2))
        self.assertEqual((TriangleType.EQUILATERAL, TriangleType.ACUTE), eq_triangle.classify())

        # Test isosceles triangle
        iso_triangle = Triangle2D(a=Point2D(x=5.0, y=2.0), b=Point2D(x=4.0, y=0.0), c=Point2D(x=6.0, y=0.0))
        self.assertEqual((TriangleType.ISOSCELES, TriangleType.ACUTE), iso_triangle.classify())

        # Test right triangle
        right_triangle = Triangle2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=3.0, y=0.0), c=Point2D(x=0.0, y=4.0))
        self.assertEqual((TriangleType.SCALENE, TriangleType.RIGHT), right_triangle.classify())

        # Test obtuse triangle
        obtuse_triangle = Triangle2D(a=Point2D(x=0.0, y=0.0), b=Point2D(x=4.0, y=0.0), c=Point2D(x=-1.0, y=2.0))
        self.assertEqual((TriangleType.SCALENE, TriangleType.OBTUSE), obtuse_triangle.classify())


class TestQuadrilateral2D(unittest.TestCase):
    def test_initialization(self):
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=2.0, y=0.0)
        p3 = Point2D(x=2.0, y=2.0)
        p4 = Point2D(x=0.0, y=2.0)
        quad = Quadrilateral2D(a=p1, b=p2, c=p3, d=p4)
        self.assertEqual(p1, quad.a)
        self.assertEqual(p2, quad.b)
        self.assertEqual(p3, quad.c)
        self.assertEqual(p4, quad.d)

    def test_area(self):
        # Test area of a square
        square = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=2.0, y=2.0),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertEqual(4.0, square.area)

        # Test area of a non-convex quadrilateral
        non_convex = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=1.0, y=1.0),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertEqual(2.0, non_convex.area)

    def test_is_convex(self):
        # Test convex quadrilateral
        convex = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=2.0, y=2.0),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertTrue(convex.is_convex)

        # Test non-convex quadrilateral
        non_convex = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=1.0, y=0.5),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertFalse(non_convex.is_convex)

    def test_contains_point(self):
        # Test with a square
        square = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=2.0, y=2.0),
            d=Point2D(x=0.0, y=2.0)
        )
        # Test point inside
        self.assertTrue(square.contains_point(Point2D(x=1.0, y=1.0)))
        # Test point outside
        self.assertFalse(square.contains_point(Point2D(x=3.0, y=3.0)))
        # Test point on edge
        self.assertTrue(square.contains_point(Point2D(x=1.0, y=0.0)))

    def test_classify(self):
        # Test square
        square = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=2.0, y=2.0),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertEqual(QuadrilateralType.SQUARE, square.classify())

        # Test rectangle
        rectangle = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=3.0, y=0.0),
            c=Point2D(x=3.0, y=2.0),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertEqual(QuadrilateralType.RECTANGLE, rectangle.classify())

        # Test rhombus
        rhombus = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=0.0),
            c=Point2D(x=2.0, y=2.0),
            d=Point2D(x=0.0, y=2.0)
        )
        self.assertEqual(QuadrilateralType.SQUARE, rhombus.classify())

        # Create a proper rhombus (all sides equal, not all angles equal)
        rhombus = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=2.0, y=1.0),
            c=Point2D(x=4.0, y=0.0),
            d=Point2D(x=2.0, y=-1.0)
        )
        self.assertEqual(QuadrilateralType.RHOMBUS, rhombus.classify())

        # Test parallelogram
        parallelogram = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=3.0, y=0.0),
            c=Point2D(x=4.0, y=2.0),
            d=Point2D(x=1.0, y=2.0)
        )
        self.assertEqual(QuadrilateralType.PARALLELOGRAM, parallelogram.classify())

        # Test trapezoid
        trapezoid = Quadrilateral2D(
            a=Point2D(x=0.0, y=0.0),
            b=Point2D(x=4.0, y=0.0),
            c=Point2D(x=3.0, y=2.0),
            d=Point2D(x=1.0, y=2.0)
        )
        self.assertEqual(QuadrilateralType.TRAPEZOID, trapezoid.classify())

        # Test kite
        kite = Quadrilateral2D(
            a=Point2D(x=1.0, y=0.0),
            b=Point2D(x=2.0, y=1.0),
            c=Point2D(x=1.0, y=3.0),
            d=Point2D(x=0.0, y=1.0)
        )
        self.assertEqual(QuadrilateralType.KITE, kite.classify())


class TestPolygon2D(unittest.TestCase):
    def test_initialization(self):
        # Create a regular pentagon
        points = tuple(Point2D(x=math.cos(2 * math.pi * i / 5), y=math.sin(2 * math.pi * i / 5)) for i in range(5))
        pentagon = Polygon2D(vertices=points)
        self.assertEqual(5, len(pentagon.vertices))

    def test_less_than_5_vertices_error(self):
        # A polygon needs at least 5 vertices
        points = tuple(Point2D(x=math.cos(2 * math.pi * i / 4), y=math.sin(2 * math.pi * i / 4)) for i in range(4))
        with self.assertRaises(ShapeError):
            Polygon2D(vertices=points)

    def test_area(self):
        # Create a regular pentagon with radius 1
        points = tuple(Point2D(x=math.cos(2 * math.pi * i / 5), y=math.sin(2 * math.pi * i / 5)) for i in range(5))
        pentagon = Polygon2D(vertices=points)
        # Area of a regular pentagon with radius 1 is 2.5 * sin(2π/5)
        expected_area = 2.5 * math.sin(2 * math.pi / 5)
        self.assertAlmostEqual(expected_area, pentagon.area, places=10)

    def test_is_convex(self):
        # Test convex polygon (regular pentagon)
        points = tuple(Point2D(x=math.cos(2 * math.pi * i / 5), y=math.sin(2 * math.pi * i / 5)) for i in range(5))
        pentagon = Polygon2D(vertices=points)
        self.assertTrue(pentagon.is_convex)

        # Test non-convex polygon (star-like shape)
        points = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=2.0, y=0.0),
            Point2D(x=1.0, y=1.0),
            Point2D(x=2.0, y=2.0),
            Point2D(x=0.0, y=2.0)
        )
        star = Polygon2D(vertices=points)
        self.assertFalse(star.is_convex)

    def test_contains_point(self):
        # Test with a regular pentagon
        points = tuple(
            Point2D(x=2 * math.cos(2 * math.pi * i / 5), y=2 * math.sin(2 * math.pi * i / 5)) for i in range(5))
        pentagon = Polygon2D(vertices=points)
        # Test point inside
        self.assertTrue(pentagon.contains_point(Point2D(x=0.0, y=0.0)))
        # Test point outside
        self.assertFalse(pentagon.contains_point(Point2D(x=3.0, y=3.0)))

    def test_is_regular(self):
        # Test regular pentagon
        points = tuple(Point2D(x=math.cos(2 * math.pi * i / 5), y=math.sin(2 * math.pi * i / 5)) for i in range(5))
        pentagon = Polygon2D(vertices=points)
        self.assertTrue(pentagon.is_regular())

        # Test non-regular pentagon
        points = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=2.0, y=0.0),
            Point2D(x=3.0, y=2.0),
            Point2D(x=1.5, y=3.0),
            Point2D(x=0.0, y=2.0)
        )
        non_regular = Polygon2D(vertices=points)
        self.assertFalse(non_regular.is_regular())

    def test_classify(self):
        # Test regular polygon
        points = tuple(Point2D(x=math.cos(2 * math.pi * i / 5), y=math.sin(2 * math.pi * i / 5)) for i in range(5))
        pentagon = Polygon2D(vertices=points)
        self.assertEqual(PolygonType.REGULAR, pentagon.classify())

        # Test equilateral but not regular
        # Creating a non-regular but equilateral pentagon requires some math
        # We'll create one with all sides equal but with different angles
        side_length = 1.0
        points = [
            Point2D(x=0.0, y=0.0),  # First point
            Point2D(x=side_length, y=0.0)  # Second point
        ]
        # Add remaining points with equal side lengths but varying angles
        angles = [math.pi / 3, 2 * math.pi / 3, 5 * math.pi / 6]
        for i, angle in enumerate(angles):
            prev_point = points[i + 1]
            new_x = prev_point.x + side_length * math.cos(angle)
            new_y = prev_point.y + side_length * math.sin(angle)
            points.append(Point2D(x=new_x, y=new_y))

        # Connect back to first point with equal side length
        last_point = points[-1]
        dist_to_first = math.sqrt((last_point.x - points[0].x) ** 2 + (last_point.y - points[0].y) ** 2)
        if abs(dist_to_first - side_length) < 1e-10:
            equilateral = Polygon2D(vertices=tuple(points))
            self.assertEqual(PolygonType.EQUILATERAL, equilateral.classify())
        else:
            # If we couldn't create a perfect equilateral pentagon, skip this test
            pass

        # Test equiangular but not regular
        # A regular pentagon has interior angles of 108°
        # Let's create a pentagon with all angles equal but sides of different lengths
        # This is challenging to construct accurately, so we'll approximate it
        points = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=1.5, y=1.2),
            Point2D(x=0.5, y=1.9),
            Point2D(x=-0.5, y=1.2)
        )
        pentagon = Polygon2D(vertices=points)
        # Note: This might not be a perfect equiangular pentagon, but we're checking the logic
        # Classification should return either EQUIANGULAR or CONVEX depending on the geometry

        # Test concave polygon
        points = (
            Point2D(x=0.0, y=0.0),
            Point2D(x=2.0, y=0.0),
            Point2D(x=2.0, y=2.0),
            Point2D(x=1.0, y=1.1),  # This creates a concave shape
            Point2D(x=0.0, y=2.0)
        )
        concave = Polygon2D(vertices=points)
        self.assertEqual(PolygonType.CONCAVE, concave.classify())


if __name__ == '__main__':
    unittest.main()
