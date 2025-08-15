#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from euler.maths.arithmetic_series import generate_arithmetic_series, sum_arithmetic_series


class TestArithmeticSeries(unittest.TestCase):
    def test_generate_arithmetic_series_basic(self):
        gen = generate_arithmetic_series(3, min_num=None, max_num=10)
        self.assertEqual(list(gen), [3, 6, 9])

    def test_generate_arithmetic_series_with_min_aligns(self):
        gen = generate_arithmetic_series(5, min_num=10, max_num=25)
        # when min is multiple, first yield is min itself (10), then increments
        self.assertEqual(list(gen), [10, 15, 20, 25])

    def test_generate_arithmetic_series_with_min_not_aligned(self):
        gen = generate_arithmetic_series(4, min_num=3, max_num=14)
        # multiples of 4 above 3 and <= 14: 4,8,12
        self.assertEqual(list(gen), [4, 8, 12])

    def test_generate_arithmetic_series_with_no_max(self):
        gen = generate_arithmetic_series(3, min_num=4, max_num=None)
        # Test stopping infinite generator manually
        series = []
        for i, num in enumerate(gen):
            if i == 5:  # Limit to 5 terms
                break
            series.append(num)
        self.assertEqual(series, [6, 9, 12, 15, 18])

    def test_generate_arithmetic_series_allow_booleans(self):
        # Test with Boolean min_num and max_num
        gen1 = generate_arithmetic_series(3, min_num=True, max_num=10)
        self.assertEqual(list(gen1), [3, 6, 9])  # True interpreted as 1

        gen2 = generate_arithmetic_series(3, min_num=None, max_num=False)
        self.assertEqual(list(gen2), [])  # False interpreted as 0, no valid terms

    def test_generate_arithmetic_series_invalid(self):
        # Non-positive common difference (zero or negative)
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(0, min_num=1, max_num=10))  # Zero common_difference
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(-5, min_num=1, max_num=10))  # Negative common_difference

        # Non-integer min_num or max_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=2.5, max_num=10))  # Float min_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=2, max_num='10'))  # String max_num

        # Invalid inputs: negative min_num and max_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=-10, max_num=10))  # Negative min_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=0, max_num=-10))  # Negative max_num

        # Valid inputs: min_num and max_num are positive integers or None
        try:
            gen = generate_arithmetic_series(3, min_num=0, max_num=10)
            self.assertEqual(list(gen), [3, 6, 9])  # Valid output
        except ValueError:
            self.fail("generate_arithmetic_series raised ValueError unexpectedly!")

        try:
            gen = generate_arithmetic_series(3, min_num=None, max_num=None)
            # Valid—but infinite, test only the first three terms
            self.assertEqual([next(gen), next(gen), next(gen)], [3, 6, 9])
        except ValueError:
            self.fail("generate_arithmetic_series raised ValueError unexpectedly!")

        try:
            gen = generate_arithmetic_series(3, min_num=None, max_num=None)
            # Valid—but infinite, test only the first three terms
            self.assertEqual([next(gen), next(gen), next(gen)], [3, 6, 9])
        except ValueError:
            self.fail("generate_arithmetic_series raised ValueError unexpectedly!")

    def test_generate_arithmetic_series_min_gt_max(self):
        # Case where min_num > max_num, should yield no terms
        gen = generate_arithmetic_series(5, min_num=20, max_num=10)
        self.assertEqual(list(gen), [])  # Expect empty list

    def test_generate_arithmetic_series_invalid_types(self):
        # Test floating-point common difference
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(2.5, min_num=2, max_num=10))  # Non-integer d

        # Test floating-point min_num and max_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=2.5, max_num=10))  # Non-integer min_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=2, max_num=10.5))  # Non-integer max_num

        # Test negative common difference
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(-3, min_num=2, max_num=10))

        # Test negative values for min_num or max_num
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=-1, max_num=10))
        with self.assertRaises(ValueError):
            list(generate_arithmetic_series(3, min_num=2, max_num=-10))

    def test_sum_arithmetic_series_by_terms(self):
        # first term 3, d=3, 4 terms -> 3 + 6 + 9 + 12 = 30
        self.assertEqual(sum_arithmetic_series(first_term=3, common_difference=3, number_of_terms=4), 30)

    def test_sum_arithmetic_series_by_limit(self):
        # <= 10 with first term 3, d=3 -> terms: 3,6,9
        # number_of_terms formula in code uses (max_limit - first_term - 1) // d
        self.assertEqual(sum_arithmetic_series(first_term=3, common_difference=3, max_limit=11), 18)

    def test_sum_arithmetic_series_invalid(self):
        with self.assertRaises(ValueError):
            sum_arithmetic_series(first_term=1, common_difference=1)  # missing required arg

    def test_sum_arithmetic_series_zero_term(self):
        self.assertEqual(sum_arithmetic_series(first_term=0, common_difference=2, number_of_terms=5), 20)

    def test_sum_arithmetic_series_no_terms_in_range(self):
        self.assertEqual(sum_arithmetic_series(first_term=100, common_difference=5, max_limit=50), 0)

    def test_sum_arithmetic_series_large_limit(self):
        # Large values with limit
        self.assertEqual(sum_arithmetic_series(first_term=1, common_difference=1, max_limit=int(1e6)), 499999500000)


if __name__ == "__main__":
    unittest.main()
