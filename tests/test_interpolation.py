#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the interpolation module.

This test suite validates the functionality of the interpolation methods defined in
the euler.utils.interpolation module, including:
- Lagrange interpolation
- Newton interpolation
- Polynomial construction and evaluation
"""

import unittest
from math import isclose

from euler.utils.interpolation import (construct_polynomial, eval_polynomial, lagrange_interpolation,
                                       newton_interpolation)


class TestInterpolation(unittest.TestCase):
    """Test cases for the interpolation module."""

    def test_lagrange_interpolation_linear(self):
        """Test Lagrange interpolation with linear data."""
        # Linear function f(x) = 2x + 1
        x_values = [1, 2, 3]
        y_values = [3, 5, 7]  # f(x) = 2x + 1

        # Test exact points
        for i, x in enumerate(x_values):
            self.assertEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=x), y_values[i])

        # Test interpolated points
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=1.5), 4.0)
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=2.5), 6.0)

    def test_lagrange_interpolation_quadratic(self):
        """Test Lagrange interpolation with quadratic data."""
        # Quadratic function f(x) = x^2
        x_values = [0, 1, 2, 3]
        y_values = [0, 1, 4, 9]  # f(x) = x^2

        # Test exact points
        for i, x in enumerate(x_values):
            self.assertEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=x), y_values[i])

        # Test interpolated points
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=1.5), 2.25)
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=2.5), 6.25)

    def test_lagrange_interpolation_validation(self):
        """Test input validation for Lagrange interpolation."""
        # Test different length x and y values
        with self.assertRaises(ValueError):
            lagrange_interpolation(x_values=[1, 2], y_values=[1, 2, 3], x=1.5)

        # Test duplicate x values
        with self.assertRaises(ValueError):
            lagrange_interpolation(x_values=[1, 2, 2], y_values=[1, 2, 3], x=1.5)

    def test_newton_interpolation_linear(self):
        """Test Newton interpolation with linear data."""
        # Linear function f(x) = 2x + 1
        x_values = [1, 2, 3]
        y_values = [3, 5, 7]  # f(x) = 2x + 1

        # Test exact points
        for i, x in enumerate(x_values):
            self.assertEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=x), y_values[i])

        # Test interpolated points
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=1.5), 4.0)
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=2.5), 6.0)

    def test_newton_interpolation_quadratic(self):
        """Test Newton interpolation with quadratic data."""
        # Quadratic function f(x) = x^2
        x_values = [0, 1, 2, 3]
        y_values = [0, 1, 4, 9]  # f(x) = x^2

        # Test exact points
        for i, x in enumerate(x_values):
            self.assertEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=x), y_values[i])

        # Test interpolated points
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=1.5), 2.25)
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=2.5), 6.25)

    def test_newton_interpolation_validation(self):
        """Test input validation for Newton interpolation."""
        # Test different length x and y values
        with self.assertRaises(ValueError):
            newton_interpolation(x_values=[1, 2], y_values=[1, 2, 3], x=1.5)

        # Test duplicate x values
        with self.assertRaises(ValueError):
            newton_interpolation(x_values=[1, 2, 2], y_values=[1, 2, 3], x=1.5)

    def test_construct_polynomial_linear(self):
        """Test polynomial construction with linear data."""
        # Linear function f(x) = 2x + 1
        x_values = [0, 1]
        y_values = [1, 3]  # f(x) = 2x + 1

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Should construct polynomial (1, 2) representing 1 + 2x
        self.assertEqual(len(poly), 2)
        self.assertAlmostEqual(poly[0], 1.0)
        self.assertAlmostEqual(poly[1], 2.0)

        # Test evaluating the polynomial at various points
        self.assertAlmostEqual(eval_polynomial(poly, 0), 1.0)
        self.assertAlmostEqual(eval_polynomial(poly, 1), 3.0)
        self.assertAlmostEqual(eval_polynomial(poly, 2), 5.0)

    def test_construct_polynomial_quadratic(self):
        """Test polynomial construction with quadratic data."""
        # Quadratic function f(x) = x^2
        x_values = [0, 1, 2]
        y_values = [0, 1, 4]  # f(x) = x^2

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Should construct polynomial (0, 0, 1) representing x^2
        self.assertEqual(len(poly), 3)
        self.assertAlmostEqual(poly[0], 0.0)
        self.assertAlmostEqual(poly[1], 0.0)
        self.assertAlmostEqual(poly[2], 1.0)

        # Test evaluating the polynomial at various points
        self.assertAlmostEqual(eval_polynomial(poly, 0), 0.0)
        self.assertAlmostEqual(eval_polynomial(poly, 1), 1.0)
        self.assertAlmostEqual(eval_polynomial(poly, 2), 4.0)
        self.assertAlmostEqual(eval_polynomial(poly, 3), 9.0)

    def test_construct_polynomial_cubic(self):
        """Test polynomial construction with cubic data."""
        # Cubic function f(x) = x^3
        x_values = [0, 1, 2, 3]
        y_values = [0, 1, 8, 27]  # f(x) = x^3

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Should construct polynomial (0, 0, 0, 1) representing x^3
        self.assertEqual(len(poly), 4)
        self.assertAlmostEqual(poly[0], 0.0)
        self.assertAlmostEqual(poly[1], 0.0)
        self.assertAlmostEqual(poly[2], 0.0)
        self.assertAlmostEqual(poly[3], 1.0)

        # Test evaluating the polynomial at various points
        self.assertAlmostEqual(eval_polynomial(poly, 0), 0.0)
        self.assertAlmostEqual(eval_polynomial(poly, 1), 1.0)
        self.assertAlmostEqual(eval_polynomial(poly, 2), 8.0)
        self.assertAlmostEqual(eval_polynomial(poly, 3), 27.0)

    def test_construct_polynomial_complex(self):
        """Test polynomial construction with more complex data."""
        # Complex function f(x) = 3x^2 - 2x + 5
        x_values = [-1, 0, 1, 2]
        y_values = [10, 5, 6, 13]  # f(x) = 3x^2 - 2x + 5

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Should construct polynomial (5, -2, 3, 0) representing 5 - 2x + 3x^2
        self.assertEqual(len(poly), 4)
        self.assertAlmostEqual(poly[0], 5.0)
        self.assertAlmostEqual(poly[1], -2.0)
        self.assertAlmostEqual(poly[2], 3.0)
        self.assertAlmostEqual(poly[3], 0.0)

        # Test evaluating the polynomial at various points
        self.assertAlmostEqual(eval_polynomial(poly, -1), 10.0)
        self.assertAlmostEqual(eval_polynomial(poly, 0), 5.0)
        self.assertAlmostEqual(eval_polynomial(poly, 1), 6.0)
        self.assertAlmostEqual(eval_polynomial(poly, 2), 13.0)

    def test_construct_polynomial_validation(self):
        """Test input validation for polynomial construction."""
        # Test different length x and y values
        with self.assertRaises(ValueError):
            construct_polynomial(x_values=[1, 2], y_values=[1, 2, 3])

        # Test duplicate x values
        with self.assertRaises(ValueError):
            construct_polynomial(x_values=[1, 2, 2], y_values=[1, 2, 3])

    def test_eval_polynomial(self):
        """Test polynomial evaluation."""
        # Test constant polynomial
        self.assertEqual(eval_polynomial((5,), 10), 5.0)

        # Test linear polynomial: 3x + 2
        self.assertEqual(eval_polynomial((2, 3), 4), 14.0)

        # Test quadratic polynomial: 2x^2 + 3x + 1
        self.assertEqual(eval_polynomial((1, 3, 2), 2), 15.0)

        # Test cubic polynomial: x^3 - 2x^2 + 3x - 4
        self.assertEqual(eval_polynomial((-4, 3, -2, 1), 3), 14.0)

    def test_methods_agreement(self):
        """Test that Lagrange and Newton interpolation agree on results."""
        # Test with various datasets
        test_cases = [
            # x_values, y_values, test_points
            ([1, 2, 3], [1, 4, 9], [1.5, 2.5, 3.5]),  # Quadratic data
            ([0, 1, 2, 3], [0, 1, 8, 27], [0.5, 1.5, 2.5]),  # Cubic data
            ([-2, -1, 0, 1, 2], [4, 1, 0, 1, 4], [-1.5, -0.5, 0.5, 1.5])  # Even function data
        ]

        for x_values, y_values, test_points in test_cases:
            for x in test_points:
                lagrange_result = lagrange_interpolation(x_values=x_values, y_values=y_values, x=x)
                newton_result = newton_interpolation(x_values=x_values, y_values=y_values, x=x)

                # Check that both methods give the same result
                self.assertTrue(
                    isclose(lagrange_result, newton_result, rel_tol=1e-9),
                    f"Lagrange: {lagrange_result}, Newton: {newton_result} at x={x}"
                )

                # If we have a polynomial constructed from the same data,
                # check that evaluating it gives the same result
                poly = construct_polynomial(x_values=x_values, y_values=y_values)
                poly_result = eval_polynomial(poly, x)

                self.assertTrue(
                    isclose(lagrange_result, poly_result, rel_tol=1e-9),
                    f"Lagrange: {lagrange_result}, Polynomial: {poly_result} at x={x}"
                )


if __name__ == '__main__':
    unittest.main()
