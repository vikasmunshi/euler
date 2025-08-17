#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from euler_solver.maths.interpolation import (
    InterpolationError,
    construct_polynomial,
    eval_polynomial,
    lagrange_interpolation,
    newton_interpolation,
)


class TestInterpolation(unittest.TestCase):
    def test_eval_polynomial_examples(self):
        # Examples from docstring
        self.assertEqual(eval_polynomial((1, 2, 1), 3), 16.0)
        self.assertEqual(eval_polynomial((5, 0, -2), 2), -3.0)
        # Additional: higher degree with negative x
        self.assertEqual(eval_polynomial((0, -1, 0, 1), -2), (-2) ** 3 - (-2))  # x^3 - x

    def test_lagrange_interpolation_errors(self):
        # Length mismatch
        with self.assertRaises(InterpolationError) as cm:
            lagrange_interpolation(x_values=[1, 2], y_values=[1], x=1.5)
        self.assertEqual(str(cm.exception), 'x_values and y_values must have the same length')
        # Duplicate x-values
        with self.assertRaises(InterpolationError) as cm:
            lagrange_interpolation(x_values=[1, 1, 2], y_values=[1, 2, 3], x=1.5)
        self.assertEqual(str(cm.exception), 'x_values must contain unique values to avoid division by zero')

    def test_lagrange_interpolation_exact_and_general(self):
        x_vals = [1, 2, 3]
        y_vals = [1, 4, 9]  # y = x^2
        # Exact match path should return the corresponding y as float
        self.assertEqual(lagrange_interpolation(x_values=x_vals, y_values=y_vals, x=2), 4.0)
        # General interpolation
        self.assertAlmostEqual(lagrange_interpolation(x_values=x_vals, y_values=y_vals, x=2.5), 6.25)

    def test_lagrange_interpolation_early_break_basis_near_zero(self):
        # Choose x very close to one of x_values to make a basis term ~ 0 and trigger early break
        x_vals = [0.0, 1.0, 2.0]
        y_vals = [0.0, 1.0, 4.0]  # y = x^2
        x = 1.0 + 1e-12  # very close to an existing node but not exactly equal
        y_expected = x * x
        y_interp = lagrange_interpolation(x_values=x_vals, y_values=y_vals, x=x)
        # Should be extremely close to the true quadratic value
        self.assertAlmostEqual(y_interp, y_expected, places=12)

    def test_newton_interpolation_errors(self):
        # Length mismatch
        with self.assertRaises(InterpolationError) as cm:
            newton_interpolation(x_values=[0, 1], y_values=[0], x=0.1)
        self.assertEqual(str(cm.exception), 'x_values and y_values must have the same length')
        # Duplicate x-values
        with self.assertRaises(InterpolationError) as cm:
            newton_interpolation(x_values=[0, 0, 1], y_values=[0, 0, 1], x=0.1)
        self.assertEqual(str(cm.exception), 'x_values must contain unique values to avoid division by zero')

    def test_newton_interpolation_matches_lagrange(self):
        x_vals = [1.0, 2.0, 3.0]
        y_vals = [1.0, 4.0, 9.0]  # y = x^2
        # Evaluate at a non-node
        x = 2.5
        self.assertAlmostEqual(
                newton_interpolation(x_values=x_vals, y_values=y_vals, x=x),
                lagrange_interpolation(x_values=x_vals, y_values=y_vals, x=x),
                places=12,
        )
        # At an exact node, Newton should evaluate to the node value as well
        self.assertEqual(newton_interpolation(x_values=x_vals, y_values=y_vals, x=2.0), 4.0)

    def test_construct_polynomial_and_evaluate(self):
        # Simple square: should produce (0.0, 0.0, 1.0)
        x_vals1 = [1, 2, 3]
        y_vals1 = [1, 4, 9]
        poly1 = construct_polynomial(x_values=x_vals1, y_values=y_vals1)
        self.assertEqual(poly1, (0.0, 0.0, 1.0))
        # Evaluate at several points
        for x in [0, 1, 2, 3, 4]:
            self.assertAlmostEqual(eval_polynomial(poly1, x), float(x * x))

        # Another quadratic: f(x) = 1 + x + x^2 through points (0,1), (1,3), (2,7)
        x_vals2 = [0, 1, 2]
        y_vals2 = [1, 3, 7]
        poly2 = construct_polynomial(x_values=x_vals2, y_values=y_vals2)
        self.assertEqual(poly2, (1.0, 1.0, 1.0))
        for x in [0, 0.5, 1, 2, -1]:
            self.assertAlmostEqual(eval_polynomial(poly2, x), float(1 + x + x * x))

    def test_construct_polynomial_errors(self):
        # Length mismatch
        with self.assertRaises(InterpolationError) as cm:
            construct_polynomial(x_values=[0, 1], y_values=[1])
        self.assertEqual(str(cm.exception), 'x_values and y_values must have the same length')
        # Duplicate x-values
        with self.assertRaises(InterpolationError) as cm:
            construct_polynomial(x_values=[0, 0, 1], y_values=[1, 1, 2])
        self.assertEqual(str(cm.exception), 'x_values must contain unique values to avoid division by zero')


if __name__ == "__main__":
    unittest.main()
