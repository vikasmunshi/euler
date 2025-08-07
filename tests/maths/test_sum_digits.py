#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the utils module."""

import unittest

from euler.maths.sum_digits import sum_digits


class TestSumDigits(unittest.TestCase):
    """Test case for word_to_num.py utility functions."""

    def test_sum_digits(self):
        """Test the sum_digits function for summing the digits of a number."""
        # Test basic examples
        self.assertEqual(sum_digits(0), 0)
        self.assertEqual(sum_digits(1), 1)
        self.assertEqual(sum_digits(9), 9)
        self.assertEqual(sum_digits(10), 1)  # 1 + 0 = 1
        self.assertEqual(sum_digits(123), 6)  # 1 + 2 + 3 = 6
        self.assertEqual(sum_digits(999), 27)  # 9 + 9 + 9 = 27

        # Test with string input
        self.assertEqual(sum_digits('0'), 0)
        self.assertEqual(sum_digits('123'), 6)
        self.assertEqual(sum_digits('999'), 27)

        # Test with larger numbers
        self.assertEqual(sum_digits(12345), 15)  # 1 + 2 + 3 + 4 + 5 = 15
        self.assertEqual(sum_digits(9876543210), 45)  # Sum of digits 0-9 = 45

        # Test with negative numbers (should count only digits, not the sign)
        self.assertEqual(sum_digits(-123), 6)  # 1 + 2 + 3 = 6
        self.assertEqual(sum_digits('-123'), 6)  # 1 + 2 + 3 = 6

        # Test with large numbers from Project Euler problems
        self.assertEqual(sum_digits(2 ** 1000), 1366)  # Known sum for 2^1000 digits
        self.assertEqual(sum_digits(10 ** 100 - 1), 900)  # 100 nines = 9 * 100 = 900

        # Test with zeros padding
        self.assertEqual(sum_digits('00123'), 6)  # Leading zeros should be counted
        self.assertEqual(sum_digits(123000), 6)  # Trailing zeros should be counted

    def test_edge_cases(self):
        """Edge cases for sum_digits"""
        self.assertEqual(sum_digits(''), 0)  # Empty string
        self.assertEqual(sum_digits('000'), 0)  # Only zeros

        # Test with very large numbers to ensure no performance issues
        large_num = '1' * 1000  # String of 1000 ones
        self.assertEqual(sum_digits(large_num), 1000)  # Should sum to 1000


if __name__ == '__main__':
    unittest.main()
