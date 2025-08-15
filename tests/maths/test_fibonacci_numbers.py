#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from euler.maths.fibonacci_numbers import (
    gen_fibonacci,
    gen_fibonacci_modulo_n,
    k_th_fibonacci_number,
    most_significant_n_digits_of_k_th_fibonacci_number,
    number_of_digits_in_k_th_fibonacci_number,
)


class TestFibonacciNumbers(unittest.TestCase):
    def test_gen_fibonacci(self):
        # Test small Fibonacci sequence
        fib_sequence = list(gen_fibonacci(10))
        self.assertEqual(fib_sequence, [1, 1, 2, 3, 5, 8])

        # Test infinite generator with a break
        generator = gen_fibonacci()
        infinite_fibs = [next(generator) for _ in range(5)]
        self.assertEqual(infinite_fibs, [1, 1, 2, 3, 5])

    def test_gen_fibonacci_modulo_n(self):
        # Test Fibonacci sequence modulo 5
        fib_mod_gen = gen_fibonacci_modulo_n(5)
        fib_mod_sequence = [next(fib_mod_gen) for _ in range(10)]
        self.assertEqual(fib_mod_sequence, [1, 1, 2, 3, 0, 3, 3, 1, 4, 0])

    def test_k_th_fibonacci_number(self):
        # Test known values
        self.assertEqual(k_th_fibonacci_number(1), 1)
        self.assertEqual(k_th_fibonacci_number(2), 1)
        self.assertEqual(k_th_fibonacci_number(3), 2)
        self.assertEqual(k_th_fibonacci_number(10), 55)

        # Test large value
        self.assertEqual(k_th_fibonacci_number(50), 12586269025)

    def test_most_significant_n_digits_of_k_th_fibonacci_number(self):
        # Test large values; ref: https://planetmath.org/listoffibonaccinumbers
        f50 = 12586269025
        f100 = 354224848179261915075
        f250 = 7896325826131730509282738943634332893686268675876375
        f500 = 139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
        for i in range(5, 12):  # not accurate after this
            self.assertEqual(most_significant_n_digits_of_k_th_fibonacci_number(50, i), int(str(f50)[:i]))
            self.assertEqual(most_significant_n_digits_of_k_th_fibonacci_number(100, i), int(str(f100)[:i]))
            self.assertEqual(most_significant_n_digits_of_k_th_fibonacci_number(250, i), int(str(f250)[:i]))
            self.assertEqual(most_significant_n_digits_of_k_th_fibonacci_number(500, i), int(str(f500)[:i]))

    def test_number_of_digits_in_k_th_fibonacci_number(self):
        # Test large values; ref: https://planetmath.org/listoffibonaccinumbers
        f50 = 12586269025
        f100 = 354224848179261915075
        f250 = 7896325826131730509282738943634332893686268675876375
        f500 = 139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
        self.assertEqual(number_of_digits_in_k_th_fibonacci_number(50), len(str(f50)))
        self.assertEqual(number_of_digits_in_k_th_fibonacci_number(100), len(str(f100)))
        self.assertEqual(number_of_digits_in_k_th_fibonacci_number(250), len(str(f250)))
        self.assertEqual(number_of_digits_in_k_th_fibonacci_number(500), len(str(f500)))

    def test_most_significant_n_digits_of_k_th_fibonacci_number_assertion(self):
        # Test assertion for invalid values of n.
        with self.assertRaises(AssertionError) as cm:
            most_significant_n_digits_of_k_th_fibonacci_number(10, 0)  # n too small
        self.assertEqual(str(cm.exception), "formula results are accurate only for n < 13")

        with self.assertRaises(AssertionError) as cm:
            most_significant_n_digits_of_k_th_fibonacci_number(10, 13)  # n too large
        self.assertEqual(str(cm.exception), "formula results are accurate only for n < 13")

    def test_gen_fibonacci_errors_and_boundaries(self):
        # Boundary: max_num < 1 should yield nothing
        self.assertEqual(list(gen_fibonacci(0)), [])
        # Error: negative max_num raises ValueError with message
        with self.assertRaises(ValueError) as cm:
            list(gen_fibonacci(-1))
        self.assertEqual(str(cm.exception), "max_num must be non-negative.")

    def test_gen_fibonacci_modulo_n_invalid(self):
        for invalid in (0, -1):
            with self.assertRaises(ValueError) as cm:
                next(gen_fibonacci_modulo_n(invalid))
            self.assertEqual(str(cm.exception), "n must be greater than 0.")

    def test_k_th_fibonacci_number_invalid(self):
        for invalid in (0, -5):
            with self.assertRaises(ValueError) as cm:
                k_th_fibonacci_number(invalid)
            self.assertEqual(str(cm.exception), "k must be greater than or equal to 1.")

    def test_most_significant_n_digits_invalid_k(self):
        with self.assertRaises(ValueError) as cm:
            most_significant_n_digits_of_k_th_fibonacci_number(0, 5)
        self.assertEqual(str(cm.exception), "k must be greater than or equal to 1.")

    def test_number_of_digits_in_k_th_fibonacci_number_invalid(self):
        with self.assertRaises(ValueError) as cm:
            number_of_digits_in_k_th_fibonacci_number(0)
        self.assertEqual(str(cm.exception), "k must be greater than or equal to 1.")


if __name__ == "__main__":
    unittest.main()
