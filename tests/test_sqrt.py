#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for the Square Root Calculation Module

This module contains unit tests for the high-precision square root calculation methods
defined in euler.utils.sqrt.
"""

import math
import unittest

from euler.utils.sqrt import SquareRootError, sqrt_binary_search, sqrt_heron_method


class TestSqrtMethods(unittest.TestCase):
    """Tests for the square root calculation methods."""

    def test_heron_method_perfect_squares(self):
        """Test sqrt_heron_method with perfect squares."""
        self.assertEqual(sqrt_heron_method(1, 1), '1')
        self.assertEqual(sqrt_heron_method(4, 1), '2')
        self.assertEqual(sqrt_heron_method(9, 1), '3')
        self.assertEqual(sqrt_heron_method(16, 2), '40')
        self.assertEqual(sqrt_heron_method(25, 2), '50')
        self.assertEqual(sqrt_heron_method(100, 2), '10')

    def test_heron_method_non_perfect_squares(self):
        """Test sqrt_heron_method with non-perfect squares."""
        # sqrt(2) ≈ 1.414213562373095...
        self.assertEqual(sqrt_heron_method(2, 10), '1414213562')
        # sqrt(3) ≈ 1.732050807568877...
        self.assertEqual(sqrt_heron_method(3, 5), '17320')
        # sqrt(5) ≈ 2.236067977499789...
        self.assertEqual(sqrt_heron_method(5, 8), '22360679')

    def test_heron_method_large_numbers(self):
        """Test sqrt_heron_method with large numbers."""
        # sqrt(10^6) = 1000
        self.assertEqual(sqrt_heron_method(10**6, 4), '1000')
        # sqrt(10^12) = 10^6
        self.assertEqual(sqrt_heron_method(10**12, 7), '1000000')

    def test_heron_method_high_precision(self):
        """Test sqrt_heron_method with high precision requirements."""
        # First 30 digits of sqrt(2)
        expected = '141421356237309504880168872420'
        self.assertEqual(sqrt_heron_method(2, 30), expected)

    def test_binary_search_perfect_squares(self):
        """Test sqrt_binary_search with perfect squares."""
        self.assertEqual(sqrt_binary_search(1, 1), '1')
        self.assertEqual(sqrt_binary_search(4, 1), '2')
        self.assertEqual(sqrt_binary_search(9, 1), '3')
        self.assertEqual(sqrt_binary_search(16, 2), '40')
        self.assertEqual(sqrt_binary_search(25, 2), '50')
        self.assertEqual(sqrt_binary_search(100, 2), '10')

    def test_binary_search_non_perfect_squares(self):
        """Test sqrt_binary_search with non-perfect squares."""
        # sqrt(2) ≈ 1.414213562373095...
        self.assertEqual(sqrt_binary_search(2, 10), '1414213562')
        # sqrt(3) ≈ 1.732050807568877...
        self.assertEqual(sqrt_binary_search(3, 5), '17320')
        # sqrt(5) ≈ 2.236067977499789...
        self.assertEqual(sqrt_binary_search(5, 8), '22360679')

    def test_binary_search_large_numbers(self):
        """Test sqrt_binary_search with large numbers."""
        # sqrt(10^6) = 1000
        self.assertEqual(sqrt_binary_search(10**6, 4), '1000')
        # sqrt(10^12) = 10^6
        self.assertEqual(sqrt_binary_search(10**12, 7), '1000000')

    def test_binary_search_high_precision(self):
        """Test sqrt_binary_search with high precision requirements."""
        # First 30 digits of sqrt(2)
        expected = '141421356237309504880168872420'
        self.assertEqual(sqrt_binary_search(2, 30), expected)

    def test_methods_equivalence(self):
        """Test that both methods produce the same results."""
        test_cases = [
            (2, 10),
            (3, 15),
            (5, 20),
            (7, 25),
            (11, 10),
            (13, 15),
            (17, 20),
            (10**6, 4),
        ]

        for number, digits in test_cases:
            heron_result = sqrt_heron_method(number, digits)
            binary_result = sqrt_binary_search(number, digits)
            self.assertEqual(heron_result, binary_result,
                             f"Methods differ for sqrt({number}) with {digits} digits")

    def test_precision_against_math_sqrt(self):
        """Compare results with math.sqrt for validation."""
        test_cases = [(2, 10), (3, 10), (5, 10), (7, 10)]

        for number, digits in test_cases:
            # Calculate expected value using math.sqrt and format to correct precision
            expected = str(math.sqrt(number)).replace('.', '')[:digits]

            # Test both methods
            heron_result = sqrt_heron_method(number, digits)
            binary_result = sqrt_binary_search(number, digits)

            # Allow small differences due to rounding in the last digit
            self.assertTrue(
                abs(int(heron_result) - int(expected)) <= 1,
                f"Heron method result {heron_result} differs from expected {expected} for sqrt({number})"
            )
            self.assertTrue(
                abs(int(binary_result) - int(expected)) <= 1,
                f"Binary search result {binary_result} differs from expected {expected} for sqrt({number})"
            )

    def test_edge_case_zero(self):
        """Test both methods with input of zero."""
        self.assertEqual(sqrt_heron_method(0, 5), '0')
        self.assertEqual(sqrt_heron_method(0, 1), '0')
        self.assertEqual(sqrt_binary_search(0, 5), '0')
        self.assertEqual(sqrt_binary_search(0, 1), '0')

    def test_negative_input_raises_square_root_error(self):
        """Test that negative inputs raise SquareRootError exception."""
        with self.assertRaises(SquareRootError):
            sqrt_heron_method(-1, 5)

        with self.assertRaises(SquareRootError):
            sqrt_heron_method(-100, 5)

        with self.assertRaises(SquareRootError):
            sqrt_binary_search(-1, 5)

        with self.assertRaises(SquareRootError):
            sqrt_binary_search(-100, 5)

        # Verify the error message contains useful information
        try:
            sqrt_heron_method(-2, 5)
        except SquareRootError as e:
            self.assertIn('-2', str(e))


if __name__ == '__main__':
    unittest.main()
