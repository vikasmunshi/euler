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

from euler.utils.interpolation import (InterpolationError, construct_polynomial, eval_polynomial,
                                       lagrange_interpolation,
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
        with self.assertRaises(InterpolationError):
            lagrange_interpolation(x_values=[1, 2], y_values=[1, 2, 3], x=1.5)

        # Test duplicate x values
        with self.assertRaises(InterpolationError):
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
        with self.assertRaises(InterpolationError):
            newton_interpolation(x_values=[1, 2], y_values=[1, 2, 3], x=1.5)

        # Test duplicate x values
        with self.assertRaises(InterpolationError):
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

        # Test polynomial construction with a higher degree polynomial (targets line 195)
        # This specifically tests the min(i, num_x_vals - 1) logic in the nested loop
        x_values = [0, 1, 2, 3, 4, 5, 6]
        y_values = [0, 1, 8, 27, 64, 125, 216]  # f(x) = x^3

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Verify polynomial correctness through evaluation
        for i, x in enumerate(x_values):
            self.assertAlmostEqual(eval_polynomial(poly, x), y_values[i])

        # Additional test with a different polynomial where i > num_x_vals - 1 in some iterations
        # This ensures the min() function is exercised in line 195
        x_values = [-3, -2, -1, 0, 1, 2, 3]
        y_values = [-27, -8, -1, 0, 1, 8, 27]  # f(x) = x^3

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Verify the expected coefficient pattern for x^3
        self.assertEqual(len(poly), 7)
        self.assertAlmostEqual(poly[0], 0.0)  # Constant term
        self.assertAlmostEqual(poly[1], 0.0)  # x term
        self.assertAlmostEqual(poly[2], 0.0)  # x^2 term
        self.assertAlmostEqual(poly[3], 1.0)  # x^3 term

    def test_construct_polynomial_validation(self):
        """Test input validation for polynomial construction."""
        # Test different length x and y values
        with self.assertRaises(InterpolationError):
            construct_polynomial(x_values=[1, 2], y_values=[1, 2, 3])

        # Test duplicate x values
        with self.assertRaises(InterpolationError):
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

    def test_extrapolation(self):
        """Test interpolation for points outside the range (extrapolation)."""
        # Linear function f(x) = 2x + 1
        x_values = [1, 2, 3]
        y_values = [3, 5, 7]  # f(x) = 2x + 1

        # Extrapolate before the first point
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=0), 1.0)
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=0), 1.0)

        # Extrapolate after the last point
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=4), 9.0)
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=4), 9.0)

    def test_numerical_stability(self):
        """Test interpolation with extreme values to check numerical stability."""
        # Test with very large x values
        x_values = [1e6, 2e6, 3e6]
        y_values = [1, 4, 9]  # Representing x^2 scaled

        # The interpolation should still follow the pattern
        x_test = 1.5e6
        expected = 2.25  # (1.5)^2

        lagrange_result = lagrange_interpolation(x_values=x_values, y_values=y_values, x=x_test)
        newton_result = newton_interpolation(x_values=x_values, y_values=y_values, x=x_test)

        self.assertAlmostEqual(lagrange_result, expected, places=2)
        self.assertAlmostEqual(newton_result, expected, places=2)

        # Test with very small x values
        x_values = [1e-6, 2e-6, 3e-6]
        y_values = [1, 4, 9]  # Same pattern

        x_test = 1.5e-6
        lagrange_result = lagrange_interpolation(x_values=x_values, y_values=y_values, x=x_test)
        newton_result = newton_interpolation(x_values=x_values, y_values=y_values, x=x_test)

        self.assertAlmostEqual(lagrange_result, expected, places=2)
        self.assertAlmostEqual(newton_result, expected, places=2)

    def test_zero_basis_optimization(self):
        """Directly test the zero basis optimization in Lagrange interpolation."""
        # Create a specific case where the basis becomes exactly zero
        # Set up points that will force the basis calculation to be zero
        x_values = [0, 1, 2, 3]
        y_values = [10, 20, 30, 40]

        # Test with x=0 to force basis=0 for some points in the calculation
        # For i=1, when calculating basis, one term will be (0-0)/(1-0) = 0
        result = lagrange_interpolation(x_values=x_values, y_values=y_values, x=0)
        self.assertEqual(result, 10.0)  # Should match y_values[0]

    def test_min_function_in_construct_polynomial(self):
        """Test the min(i, num_x_vals - 1) expression in construct_polynomial."""
        # Set up a case where i will be greater than num_x_vals - 1 in some iterations
        # This specifically targets line 195 where min(i, num_x_vals - 1) is used

        # Use a large set of points to ensure various values of i are used
        x_values = [0, 1, 2, 3, 4, 5]
        y_values = [0, 1, 8, 27, 64, 125]  # f(x) = x^3

        poly = construct_polynomial(x_values=x_values, y_values=y_values)

        # Check the expected coefficients for a cubic polynomial
        self.assertEqual(len(poly), 6)
        # For a perfect cubic, only the x^3 term should be non-zero (with small floating point errors possible)
        self.assertAlmostEqual(poly[0], 0.0, places=10)  # Constant term
        self.assertAlmostEqual(poly[1], 0.0, places=10)  # x term
        self.assertAlmostEqual(poly[2], 0.0, places=10)  # x^2 term
        self.assertAlmostEqual(poly[3], 1.0, places=10)  # x^3 term

    def test_polynomial_construction_various_degrees(self):
        # Create polynomials of different degrees to trigger different paths in the code
        test_cases = [
            # x_values, y_values, expected coefficients, description
            (
                [-2, -1, ],  # x values
                [16, 1, ],  # y values (representing x^4)
                (0.0, 0.0, 0.0, 0.0, 1.0),  # expected coefficients
                "Quartic polynomial 2 points"
            ),
            (
                [-2, -1, 0, 1, 2, 3, 4, 5],  # x values
                [16, 1, 0, 1, 16, 81, 256, 625],  # y values (representing x^4)
                (0.0, 0.0, 0.0, 0.0, 1.0),  # expected coefficients
                "Quartic polynomial 8 points"
            ),
            (
                [-3, -2, -1, 0, 1, 2, 3, 4, 5],  # x values
                [-243, -32, -1, 0, 1, 32, 243, 1024, 3125],  # y values (representing x^5)
                (0.0, 0.0, 0.0, 0.0, 0.0, 1.0),  # expected coefficients for x^5
                "Quintic polynomial 9 points"
            ),
            (
                [-3, ],  # x values
                [-243, ],  # y values (representing x^5)
                (0.0, 0.0, 0.0, 0.0, 0.0, 1.0),  # expected coefficients for x^5
                "Quintic polynomial 1 point"
            ),
        ]

        for x_values, y_values, expected_coeffs, desc in test_cases:
            poly = construct_polynomial(x_values=x_values, y_values=y_values)

            # Check polynomial length
            self.assertEqual(len(poly), len(x_values), f"{desc}: incorrect length")

            # Check polynomial
            for x, y in zip(x_values, y_values):
                self.assertAlmostEqual(eval_polynomial(poly, x), y, places=10,
                                       msg=f"{desc}: incorrect value at x={x}")

    def test_interpolation(self):
        # Test exact match in lagrange interpolation
        x_values = [1, 2, 3, 4]
        y_values = [1, 4, 9, 16]
        # Test when x exactly matches one of the input points
        self.assertEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=2), 4.0)

        # Two points (linear interpolation)
        x_values = [0, 10]
        y_values = [5, 15]  # f(x) = x + 5

        # Test exact interpolation
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=5), 10.0)
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=5), 10.0)

        # Near-boundary case
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_values, y_values=y_values, x=0.001), 5.001)
        self.assertAlmostEqual(newton_interpolation(x_values=x_values, y_values=y_values, x=9.999), 14.999)

    def test_early_exit_optimization(self):
        """Test the early exit optimization in Lagrange interpolation when basis becomes zero."""
        # Test case designed to trigger isclose(basis, 0.0, abs_tol=1e-10) condition
        # Create a scenario where basis becomes very close to zero
        x_values = [-9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        y_values = [-729, -512, -343, -216, -125, -64, -27, -8, -1, 0, 1, 8, 27, 64, 125, 216, 343, 512, 729]

        # When x is very close to 0 but not exactly 0, the basis computation for
        # some points will be very close to zero (but not exactly zero)
        # This will trigger the isclose check
        x = 1e-11  # Very close to zero, but not exactly zero
        result = lagrange_interpolation(x_values=x_values, y_values=y_values, x=x)

        # The expected result should be very close to 0
        self.assertAlmostEqual(result, 0.0, places=7,
                               msg="Lagrange interpolation with near-zero basis should return correct value")

        # Also test with standard cases to maintain existing test coverage
        x_values = [0, 1, 2, 3, 4, 5]
        y_values = [0, 1, 8, 27, 64, 125]
        for x, y in ((0, 0), (1, 1), (2, 8), (3, 27), (4, 64), (5, 125)):
            evaluated_y = lagrange_interpolation(x_values=x_values, y_values=y_values, x=x)
            self.assertAlmostEqual(evaluated_y, y, places=10)


if __name__ == '__main__':
    unittest.main()
