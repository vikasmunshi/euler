#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the polynomial_numbers module."""

import unittest
from unittest.mock import patch

from euler.logger import logger
from euler.maths.polynomial_numbers import (FigurateNumber, NumberError, closest_heptagonal_number,
                                            closest_hexagonal_number, closest_octagonal_number,
                                            closest_pentagonal_number, closest_square_number, closest_triangle_number,
                                            is_heptagonal_number, is_hexagonal_number, is_octagonal_number,
                                            is_pentagonal_number, is_square_number, is_triangle_number, main,
                                            nth_heptagonal_number, nth_hexagonal_number, nth_octagonal_number,
                                            nth_pentagonal_number, nth_square_number, nth_triangle_number, p_gen)


class TestPolynomialNumbers(unittest.TestCase):
    """Test case for polynomial_numbers.py utility functions."""

    def test_triangle_numbers(self):
        """Test triangle number functions."""
        # Test nth_triangle_number
        self.assertEqual(nth_triangle_number(1), 1)
        self.assertEqual(nth_triangle_number(2), 3)
        self.assertEqual(nth_triangle_number(3), 6)
        self.assertEqual(nth_triangle_number(4), 10)
        self.assertEqual(nth_triangle_number(5), 15)
        self.assertEqual(nth_triangle_number(10), 55)
        self.assertEqual(nth_triangle_number(100), 5050)

        # Test is_triangle_number
        self.assertTrue(is_triangle_number(1))
        self.assertTrue(is_triangle_number(3))
        self.assertTrue(is_triangle_number(6))
        self.assertTrue(is_triangle_number(10))
        self.assertTrue(is_triangle_number(15))
        self.assertTrue(is_triangle_number(55))
        self.assertFalse(is_triangle_number(2))
        self.assertFalse(is_triangle_number(4))
        self.assertFalse(is_triangle_number(7))
        self.assertFalse(is_triangle_number(11))

        # Test closest_triangle_number
        index, lower, upper = closest_triangle_number(7)
        self.assertAlmostEqual(index, 3.27492, places=5)
        self.assertEqual(lower, 6)
        self.assertEqual(upper, 10)

        index, lower, upper = closest_triangle_number(10)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 10)
        self.assertEqual(upper, 10)

        index, lower, upper = closest_triangle_number(20)
        self.assertAlmostEqual(index, 5.84429, places=5)
        self.assertEqual(lower, 15)
        self.assertEqual(upper, 21)

    def test_square_numbers(self):
        """Test square number functions."""
        # Test nth_square_number
        self.assertEqual(nth_square_number(1), 1)
        self.assertEqual(nth_square_number(2), 4)
        self.assertEqual(nth_square_number(3), 9)
        self.assertEqual(nth_square_number(4), 16)
        self.assertEqual(nth_square_number(5), 25)
        self.assertEqual(nth_square_number(10), 100)
        self.assertEqual(nth_square_number(100), 10000)

        # Test is_square_number
        self.assertTrue(is_square_number(1))
        self.assertTrue(is_square_number(4))
        self.assertTrue(is_square_number(9))
        self.assertTrue(is_square_number(16))
        self.assertTrue(is_square_number(25))
        self.assertTrue(is_square_number(100))
        self.assertFalse(is_square_number(2))
        self.assertFalse(is_square_number(3))
        self.assertFalse(is_square_number(5))
        self.assertFalse(is_square_number(10))

        # Test closest_square_number
        # Test with a perfect square
        index, lower, upper = closest_square_number(16)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 16)
        self.assertEqual(upper, 16)

        # Test with a value between squares
        index, lower, upper = closest_square_number(8)
        self.assertAlmostEqual(index, 2.82843, places=5)  # sqrt(8)
        self.assertEqual(lower, 4)  # 2²
        self.assertEqual(upper, 9)  # 3²

        # Test with a value just above a square
        index, lower, upper = closest_square_number(10)
        self.assertAlmostEqual(index, 3.16228, places=5)  # sqrt(10)
        self.assertEqual(lower, 9)  # 3²
        self.assertEqual(upper, 16)  # 4²

        # Test with a value just below a square
        index, lower, upper = closest_square_number(15)
        self.assertAlmostEqual(index, 3.87298, places=5)  # sqrt(15)
        self.assertEqual(lower, 9)  # 3²
        self.assertEqual(upper, 16)  # 4²

        # Test with a large number
        index, lower, upper = closest_square_number(10000)
        self.assertEqual(index, 100.0)
        self.assertEqual(lower, 10000)  # 100²
        self.assertEqual(upper, 10000)  # 100²

        # Test closest_square_number
        index, lower, upper = closest_square_number(8)
        self.assertAlmostEqual(index, 2.82843, places=5)
        self.assertEqual(lower, 4)
        self.assertEqual(upper, 9)

        index, lower, upper = closest_square_number(16)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 16)
        self.assertEqual(upper, 16)

        index, lower, upper = closest_square_number(20)
        self.assertAlmostEqual(index, 4.47214, places=5)
        self.assertEqual(lower, 16)
        self.assertEqual(upper, 25)

    def test_pentagonal_numbers(self):
        """Test pentagonal number functions."""
        # Test nth_pentagonal_number
        self.assertEqual(nth_pentagonal_number(1), 1)
        self.assertEqual(nth_pentagonal_number(2), 5)
        self.assertEqual(nth_pentagonal_number(3), 12)
        self.assertEqual(nth_pentagonal_number(4), 22)
        self.assertEqual(nth_pentagonal_number(5), 35)
        self.assertEqual(nth_pentagonal_number(10), 145)

        # Test is_pentagonal_number
        self.assertTrue(is_pentagonal_number(1))
        self.assertTrue(is_pentagonal_number(5))
        self.assertTrue(is_pentagonal_number(12))
        self.assertTrue(is_pentagonal_number(22))
        self.assertTrue(is_pentagonal_number(35))
        self.assertTrue(is_pentagonal_number(145))
        self.assertFalse(is_pentagonal_number(2))
        self.assertFalse(is_pentagonal_number(3))
        self.assertFalse(is_pentagonal_number(6))
        self.assertFalse(is_pentagonal_number(13))

        # Test closest_pentagonal_number
        index, lower, upper = closest_pentagonal_number(20)
        self.assertAlmostEqual(index, 3.82195, places=5)
        self.assertEqual(lower, 12)
        self.assertEqual(upper, 22)

        index, lower, upper = closest_pentagonal_number(22)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 22)
        self.assertEqual(upper, 22)

        index, lower, upper = closest_pentagonal_number(30)
        self.assertAlmostEqual(index, 4.64191, places=5)
        self.assertEqual(lower, 22)
        self.assertEqual(upper, 35)

    def test_hexagonal_numbers(self):
        """Test hexagonal number functions."""
        # Test nth_hexagonal_number
        self.assertEqual(nth_hexagonal_number(1), 1)
        self.assertEqual(nth_hexagonal_number(2), 6)
        self.assertEqual(nth_hexagonal_number(3), 15)
        self.assertEqual(nth_hexagonal_number(4), 28)
        self.assertEqual(nth_hexagonal_number(5), 45)
        self.assertEqual(nth_hexagonal_number(10), 190)

        # Test is_hexagonal_number
        self.assertTrue(is_hexagonal_number(1))
        self.assertTrue(is_hexagonal_number(6))
        self.assertTrue(is_hexagonal_number(15))
        self.assertTrue(is_hexagonal_number(28))
        self.assertTrue(is_hexagonal_number(45))
        self.assertTrue(is_hexagonal_number(190))
        self.assertFalse(is_hexagonal_number(2))
        self.assertFalse(is_hexagonal_number(3))
        self.assertFalse(is_hexagonal_number(7))
        self.assertFalse(is_hexagonal_number(16))

        # Test closest_hexagonal_number
        index, lower, upper = closest_hexagonal_number(20)
        self.assertAlmostEqual(index, 3.42214438511238, places=5)
        self.assertEqual(lower, 15)
        self.assertEqual(upper, 28)

        index, lower, upper = closest_hexagonal_number(28)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 28)
        self.assertEqual(upper, 28)

        index, lower, upper = closest_hexagonal_number(35)
        self.assertAlmostEqual(index, 4.440763653560053, places=5)
        self.assertEqual(lower, 28)
        self.assertEqual(upper, 45)

    def test_heptagonal_numbers(self):
        """Test heptagonal number functions."""
        # Test nth_heptagonal_number
        self.assertEqual(nth_heptagonal_number(1), 1)
        self.assertEqual(nth_heptagonal_number(2), 7)
        self.assertEqual(nth_heptagonal_number(3), 18)
        self.assertEqual(nth_heptagonal_number(4), 34)
        self.assertEqual(nth_heptagonal_number(5), 55)
        self.assertEqual(nth_heptagonal_number(10), 235)

        # Test is_heptagonal_number
        self.assertTrue(is_heptagonal_number(1))
        self.assertTrue(is_heptagonal_number(7))
        self.assertTrue(is_heptagonal_number(18))
        self.assertTrue(is_heptagonal_number(34))
        self.assertTrue(is_heptagonal_number(55))
        self.assertTrue(is_heptagonal_number(235))
        self.assertFalse(is_heptagonal_number(2))
        self.assertFalse(is_heptagonal_number(3))
        self.assertFalse(is_heptagonal_number(8))
        self.assertFalse(is_heptagonal_number(19))

        # Test closest_heptagonal_number
        index, lower, upper = closest_heptagonal_number(20)
        self.assertAlmostEqual(index, 3.1442925306655782, places=5)
        self.assertEqual(lower, 18)
        self.assertEqual(upper, 34)

        index, lower, upper = closest_heptagonal_number(34)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 34)
        self.assertEqual(upper, 34)

        index, lower, upper = closest_heptagonal_number(40)
        self.assertAlmostEqual(index, 4.311234224026316, places=5)
        self.assertEqual(lower, 34)
        self.assertEqual(upper, 55)

    def test_octagonal_numbers(self):
        """Test octagonal number functions."""
        # Test nth_octagonal_number
        self.assertEqual(nth_octagonal_number(1), 1)
        self.assertEqual(nth_octagonal_number(2), 8)
        self.assertEqual(nth_octagonal_number(3), 21)
        self.assertEqual(nth_octagonal_number(4), 40)
        self.assertEqual(nth_octagonal_number(5), 65)
        self.assertEqual(nth_octagonal_number(10), 280)

        # Test is_octagonal_number
        self.assertTrue(is_octagonal_number(1))
        self.assertTrue(is_octagonal_number(8))
        self.assertTrue(is_octagonal_number(21))
        self.assertTrue(is_octagonal_number(40))
        self.assertTrue(is_octagonal_number(65))
        self.assertTrue(is_octagonal_number(280))
        self.assertFalse(is_octagonal_number(2))
        self.assertFalse(is_octagonal_number(3))
        self.assertFalse(is_octagonal_number(9))
        self.assertFalse(is_octagonal_number(22))

        # Test closest_octagonal_number
        index, lower, upper = closest_octagonal_number(25)
        self.assertAlmostEqual(index, 3.23927, places=5)
        self.assertEqual(lower, 21)
        self.assertEqual(upper, 40)

        index, lower, upper = closest_octagonal_number(40)
        self.assertEqual(index, 4.0)
        self.assertEqual(lower, 40)
        self.assertEqual(upper, 40)

        index, lower, upper = closest_octagonal_number(50)
        self.assertAlmostEqual(index, 4.42940, places=5)
        self.assertEqual(lower, 40)
        self.assertEqual(upper, 65)

    def test_figurate_number_class(self):
        """Test the FigurateNumber class."""
        # Test FigurateNumber constants
        self.assertEqual(FigurateNumber.TRIANGLE.value, 3)
        self.assertEqual(FigurateNumber.SQUARE.value, 4)
        self.assertEqual(FigurateNumber.PENTAGONAL.value, 5)
        self.assertEqual(FigurateNumber.HEXAGONAL.value, 6)
        self.assertEqual(FigurateNumber.HEPTAGONAL.value, 7)
        self.assertEqual(FigurateNumber.OCTAGONAL.value, 8)

        # Test __str__ method
        self.assertEqual(str(FigurateNumber.TRIANGLE), "Triangle")
        self.assertEqual(str(FigurateNumber.SQUARE), "Square")
        self.assertEqual(str(FigurateNumber.PENTAGONAL), "Pentagonal")
        self.assertEqual(str(FigurateNumber.HEXAGONAL), "Hexagonal")
        self.assertEqual(str(FigurateNumber.HEPTAGONAL), "Heptagonal")
        self.assertEqual(str(FigurateNumber.OCTAGONAL), "Octagonal")

    def test_input_validation(self):
        """Test input validation for polynomial functions."""
        # Test with invalid inputs (negative or zero)
        with self.assertRaises(NumberError):
            nth_triangle_number(0)
        with self.assertRaises(NumberError):
            nth_triangle_number(-1)

        with self.assertRaises(NumberError):
            nth_square_number(0)
        with self.assertRaises(NumberError):
            nth_square_number(-5)

        with self.assertRaises(NumberError):
            nth_pentagonal_number(0)
        with self.assertRaises(NumberError):
            nth_pentagonal_number(-10)

        with self.assertRaises(NumberError):
            nth_hexagonal_number(0)
        with self.assertRaises(NumberError):
            nth_hexagonal_number(-2)

        with self.assertRaises(NumberError):
            nth_heptagonal_number(0)
        with self.assertRaises(NumberError):
            nth_heptagonal_number(-3)

        with self.assertRaises(NumberError):
            nth_octagonal_number(0)
        with self.assertRaises(NumberError):
            nth_octagonal_number(-4)

        # Test with invalid inputs for is_ functions
        with self.assertRaises(NumberError):
            is_triangle_number(-1)
        with self.assertRaises(NumberError):
            is_square_number(-4)
        with self.assertRaises(NumberError):
            is_pentagonal_number(-5)
        with self.assertRaises(NumberError):
            is_hexagonal_number(-6)
        with self.assertRaises(NumberError):
            is_heptagonal_number(-7)
        with self.assertRaises(NumberError):
            is_octagonal_number(-8)

        # Test with invalid inputs for closest_ functions
        with self.assertRaises(NumberError):
            closest_triangle_number(0)
        with self.assertRaises(NumberError):
            closest_square_number(-9)
        with self.assertRaises(NumberError):
            closest_pentagonal_number(0)
        with self.assertRaises(NumberError):
            closest_hexagonal_number(-16)
        with self.assertRaises(NumberError):
            closest_heptagonal_number(0)
        with self.assertRaises(NumberError):
            closest_octagonal_number(-25)

    def test_large_numbers(self):
        """Test with larger polynomial numbers."""
        # Test with larger numbers
        self.assertEqual(nth_triangle_number(1000), 500500)
        self.assertEqual(nth_square_number(500), 250000)
        self.assertEqual(nth_pentagonal_number(300), 134850)
        self.assertEqual(nth_hexagonal_number(200), 79800)
        self.assertEqual(nth_heptagonal_number(150), 56025)
        self.assertEqual(nth_octagonal_number(100), 29800)

        # Test large is_ functions
        self.assertTrue(is_triangle_number(500500))
        self.assertTrue(is_square_number(250000))
        self.assertTrue(is_pentagonal_number(134850))
        self.assertTrue(is_hexagonal_number(1999000))
        self.assertTrue(is_heptagonal_number(2114620))
        self.assertTrue(is_octagonal_number(2428200))

        # Test large non-polynomial numbers
        self.assertFalse(is_triangle_number(500501))
        self.assertFalse(is_square_number(250001))
        self.assertFalse(is_pentagonal_number(134851))
        self.assertFalse(is_hexagonal_number(119801))
        self.assertFalse(is_heptagonal_number(111226))
        self.assertFalse(is_octagonal_number(98901))

    def test_special_cases(self):
        """Test special cases and edge conditions."""
        # All figurate numbers include 1 as their first term
        self.assertTrue(is_triangle_number(1))
        self.assertTrue(is_square_number(1))
        self.assertTrue(is_pentagonal_number(1))
        self.assertTrue(is_hexagonal_number(1))
        self.assertTrue(is_heptagonal_number(1))
        self.assertTrue(is_octagonal_number(1))

        # Test matching numbers between different sequences
        # 36 is both triangular and square
        self.assertTrue(is_triangle_number(36))
        self.assertTrue(is_square_number(36))

        # 1225 is both square and pentagonal
        self.assertTrue(is_square_number(1225))
        self.assertTrue(is_pentagonal_number(1335))

        # 1 is all figurate numbers
        self.assertEqual(nth_triangle_number(1), 1)
        self.assertEqual(nth_square_number(1), 1)
        self.assertEqual(nth_pentagonal_number(1), 1)
        self.assertEqual(nth_hexagonal_number(1), 1)
        self.assertEqual(nth_heptagonal_number(1), 1)
        self.assertEqual(nth_octagonal_number(1), 1)

    def test_p_gen(self):
        """Test p_gen generator function."""
        # Test generating triangle numbers in a range
        from euler.maths.polynomial_numbers import p_gen, FigurateNumber

        triangle_nums = list(p_gen(FigurateNumber.TRIANGLE, 10, 30))
        self.assertEqual(triangle_nums, [10, 15, 21, 28])  # Triangle numbers between 10 and 30

        # Test generating square numbers in a range
        square_nums = list(p_gen(FigurateNumber.SQUARE, 20, 100))
        self.assertEqual(square_nums, [25, 36, 49, 64, 81, 100])  # Square numbers between 20 and 100

        # Test generating pentagonal numbers in a range
        pent_nums = list(p_gen(FigurateNumber.PENTAGONAL, 50, 100))
        self.assertEqual(pent_nums, [51, 70, 92])  # Pentagonal numbers between 50 and 100

        # Test empty range (min > max)
        self.assertEqual(list(p_gen(FigurateNumber.TRIANGLE, 100, 10)), [])

        # Test min equals max for exact value
        hex_nums = list(p_gen(FigurateNumber.HEXAGONAL, 67, 67))
        self.assertEqual(hex_nums, [])  # No exact hexagonal number 67

        # Test with a value that is a hexagonal number
        hex_nums = list(p_gen(FigurateNumber.HEXAGONAL, 28, 28))
        self.assertEqual(hex_nums, [28])  # Exactly one hexagonal number 28

        # Test large range with few numbers
        oct_nums = list(p_gen(FigurateNumber.OCTAGONAL, 1000, 2000))
        self.assertEqual(oct_nums, [1045, 1160, 1281, 1408, 1541, 1680, 1825, 1976])  # Octagonal numbers 1000 to 2000

        # Test minimum value boundary
        hept_nums = list(p_gen(FigurateNumber.HEPTAGONAL, 1, 50))
        self.assertEqual(hept_nums, [1, 7, 18, 34])  # Heptagonal numbers from 1 to 50

        # Test empty result
        self.assertEqual(list(p_gen(FigurateNumber.TRIANGLE, 4, 5)), [])  # No triangle numbers between 4 and 5

    def test_main_function(self):
        """Test the main function returns 0 when all validations pass."""
        # The main function should return 0 when all tests pass
        logger.setLevel("CRITICAL")
        result = main()
        self.assertEqual(result, 0, "The main function should return 0 when all validations pass")

    def test_main_function_v_func_errors(self):
        """Test error paths in the main function, ensuring they result in failure."""
        logger.setLevel("CRITICAL")
        for to_mock in (is_triangle_number, is_square_number, is_pentagonal_number,
                        is_hexagonal_number, is_heptagonal_number, is_octagonal_number):
            with patch(f'euler.maths.polynomial_numbers.{to_mock.__name__}') as mocked:
                mocked.__name__ = f'mocked_{to_mock.__name__}'

                # Mock the function behavior for controlled testing
                def mock_behavior(n):
                    return not to_mock(n)

                mocked.side_effect = mock_behavior
                result = main()
                self.assertGreater(result, 0, "The main function should capture errors in validations")

    def test_main_function_c_func_errors(self):
        """Test error paths in the main function, ensuring they result in failure."""
        logger.setLevel("CRITICAL")
        for to_mock in (closest_triangle_number, closest_square_number,
                        closest_pentagonal_number, closest_hexagonal_number,
                        closest_heptagonal_number, closest_octagonal_number):
            with patch(f'euler.maths.polynomial_numbers.{to_mock.__name__}') as mocked:
                mocked.__name__ = f'mocked_{to_mock.__name__}'

                # Mock the function behavior for controlled testing
                def mock_behavior(n):
                    return to_mock(n + 1)

                mocked.side_effect = mock_behavior
                result = main()
                self.assertGreater(result, 0, "The main function should capture errors in validations")

    def test_main_function_p_gen_errors(self):
        """Test error paths in the main function, ensuring they result in failure."""
        logger.setLevel("CRITICAL")
        to_mock = p_gen
        with patch('euler.maths.polynomial_numbers.p_gen') as mocked:
            mocked.__name__ = f'mocked_{to_mock.__name__}'

            # Mock the function behavior for controlled testing
            def mock_behavior(*args, **kwargs):
                yield 1
                yield from to_mock(*args, **kwargs)

            mocked.side_effect = mock_behavior
            result = main()
            self.assertGreater(result, 0, "The main function should capture errors in validations")


if __name__ == '__main__':
    unittest.main()
