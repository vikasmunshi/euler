#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the misc module."""

import unittest

from euler.utils.misc import sum_digits, word_to_num


class TestMisc(unittest.TestCase):
    """Test case for misc.py utility functions."""

    def test_word_to_num(self):
        """Test the word_to_num function for converting words to their alphabetical value."""
        # Test basic examples
        self.assertEqual(word_to_num('A'), 1)
        self.assertEqual(word_to_num('Z'), 26)
        self.assertEqual(word_to_num('COLIN'), 53)  # C(3) + O(15) + L(12) + I(9) + N(14) = 53

        # Test with common names
        self.assertEqual(word_to_num('PETER'), 64)  # P(16) + E(5) + T(20) + E(5) + R(18) = 64
        self.assertEqual(word_to_num('MARY'), 57)   # M(13) + A(1) + R(18) + Y(25) = 57

        # Test with quotes that should be stripped
        self.assertEqual(word_to_num('"COLIN"'), 53)
        self.assertEqual(word_to_num('"PETER"'), 64)

        # Test with single letters
        for i, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 1):
            self.assertEqual(word_to_num(letter), i)

        # Test with empty string and whitespace
        self.assertEqual(word_to_num(''), 0)
        self.assertEqual(word_to_num(' '), 0)  # Space is not counted

        # Test with lowercase (should be case-sensitive, A=1, a=97 in ASCII)
        self.assertNotEqual(word_to_num('a'), 1)
        self.assertNotEqual(word_to_num('colin'), word_to_num('COLIN'))

        # Test with longer words from Project Euler problems
        self.assertEqual(word_to_num('MATHEMATICS'), 112)
        self.assertEqual(word_to_num('EULER'), 61)
        self.assertEqual(word_to_num('PROJECT'), 87)

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
        self.assertEqual(sum_digits(2**1000), 1366)  # Known sum for 2^1000 digits
        self.assertEqual(sum_digits(10**100 - 1), 900)  # 100 nines = 9 * 100 = 900

        # Test with zeros padding
        self.assertEqual(sum_digits('00123'), 6)  # Leading zeros should be counted
        self.assertEqual(sum_digits(123000), 6)  # Trailing zeros should be counted

    def test_edge_cases(self):
        """Test edge cases for both functions."""
        # Edge cases for word_to_num
        self.assertEqual(word_to_num('""'), 0)  # Empty string with quotes
        self.assertEqual(word_to_num('   '), 0)  # Only whitespace

        # Check that symbols don't contribute to the sum in word_to_num
        # Non-alphabet characters might produce unexpected results based on ASCII values
        self.assertNotEqual(word_to_num('A-Z'), word_to_num('AZ'))

        # Edge cases for sum_digits
        self.assertEqual(sum_digits(''), 0)  # Empty string
        self.assertEqual(sum_digits('000'), 0)  # Only zeros

        # Test with very large numbers to ensure no performance issues
        large_num = '1' * 1000  # String of 1000 ones
        self.assertEqual(sum_digits(large_num), 1000)  # Should sum to 1000


if __name__ == '__main__':
    unittest.main()
