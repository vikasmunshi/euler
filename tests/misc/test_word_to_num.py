#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the misc module."""

import unittest

from euler.misc.word_to_num import word_to_num


class TestMisc(unittest.TestCase):
    """Test case for word_to_num.py utility functions."""

    def test_word_to_num(self):
        """Test the word_to_num function for converting words to their alphabetical value."""
        # Test basic examples
        self.assertEqual(word_to_num('A'), 1)
        self.assertEqual(word_to_num('Z'), 26)
        self.assertEqual(word_to_num('COLIN'), 53)  # C(3) + O(15) + L(12) + I(9) + N(14) = 53

        # Test with common names
        self.assertEqual(word_to_num('PETER'), 64)  # P(16) + E(5) + T(20) + E(5) + R(18) = 64
        self.assertEqual(word_to_num('MARY'), 57)  # M(13) + A(1) + R(18) + Y(25) = 57

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

    def test_edge_cases(self):
        """Edge cases for word_to_num"""
        self.assertEqual(word_to_num('""'), 0)  # Empty string with quotes
        self.assertEqual(word_to_num('   '), 0)  # Only whitespace

        # Check that symbols don't contribute to the sum in word_to_num
        # Non-alphabet characters might produce unexpected results based on ASCII values
        self.assertNotEqual(word_to_num('A-Z'), word_to_num('AZ'))


if __name__ == '__main__':
    unittest.main()
