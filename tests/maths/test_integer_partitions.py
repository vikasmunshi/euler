#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from euler_solver.maths.integer_partitions import (
    IntegerPartitionError,
    get_partitions_simple_recursion,
    get_prime_partitions_simple_recursion,
    main,
    num_partitions_simple_recursion,
    num_partitions_recursive,
    num_prime_partitions_simple_recursion,
)


class TestIntegerPartitions(unittest.TestCase):
    def test_num_partitions_known_values(self):
        # Known partition numbers p(n) for n = 0..10
        known = {
            -5: 0,  # negative returns 0
            0: 1,
            1: 1,
            2: 2,
            3: 3,
            4: 5,
            5: 7,
            6: 11,
            7: 15,
            8: 22,
            9: 30,
            10: 42,
        }
        for n, expected in known.items():
            with self.subTest(n=n):
                self.assertEqual(num_partitions_recursive(n), expected)

    def test_num_integer_partitions_unconstrained_matches_num_partitions(self):
        # When slots == number, the constrained count should equal p(n)
        for n in range(1, 11):
            with self.subTest(n=n):
                self.assertEqual(num_partitions_simple_recursion(number=n, slots=n), num_partitions_recursive(n))

    def test_num_integer_partitions_with_slot_constraint(self):
        # Example from docstring: 5 with slots=3 -> 5
        self.assertEqual(num_partitions_simple_recursion(number=5, slots=3), 5)

    def test_num_integer_partitions_errors_and_boundaries(self):
        # Negative inputs
        with self.assertRaises(IntegerPartitionError) as cm:
            num_partitions_simple_recursion(number=-1, slots=0)
        self.assertEqual(str(cm.exception), 'number and slots must be non-negative')

        with self.assertRaises(IntegerPartitionError) as cm:
            num_partitions_simple_recursion(number=0, slots=-1)
        self.assertEqual(str(cm.exception), 'number and slots must be non-negative')

        # number < slots error
        with self.assertRaises(IntegerPartitionError) as cm:
            num_partitions_simple_recursion(number=3, slots=4)
        self.assertEqual(str(cm.exception), 'number must be greater than or equal to slots')

        # Boundary: number <= 1 returns number (with valid slots)
        self.assertEqual(num_partitions_simple_recursion(number=0, slots=0), 0)
        self.assertEqual(num_partitions_simple_recursion(number=1, slots=1), 1)

    def test_get_partitions_examples(self):
        # Exact lists from docstring examples
        self.assertEqual(
                get_partitions_simple_recursion(number=4, slots=4),
                [[1, 1, 1, 1], [2, 1, 1], [2, 2], [3, 1], [4]],
        )
        self.assertEqual(
                get_partitions_simple_recursion(number=4, slots=2),
                [[1, 1, 1, 1], [2, 1, 1], [2, 2]],
        )
        # Verify sums and ordering are as expected for another small case
        parts_5 = get_partitions_simple_recursion(number=5, slots=5)
        self.assertEqual(len(parts_5), num_partitions_recursive(5))
        for p in parts_5:
            self.assertEqual(sum(p), 5)

    def test_get_partitions_errors_and_boundaries(self):
        # OverflowError with exact message format
        with self.assertRaises(OverflowError) as cm:
            get_partitions_simple_recursion(number=6, slots=6, safe_limit=5)
        self.assertEqual(str(cm.exception), 'number must be less than safe_limit=5')

        # Negative / number < slots errors
        with self.assertRaises(IntegerPartitionError) as cm:
            get_partitions_simple_recursion(number=-1, slots=0)
        self.assertEqual(str(cm.exception), 'number and slots must be non-negative')

        with self.assertRaises(IntegerPartitionError) as cm:
            get_partitions_simple_recursion(number=3, slots=4)
        self.assertEqual(str(cm.exception), 'number must be greater than or equal to slots')

        # number == 0 returns []
        self.assertEqual(get_partitions_simple_recursion(number=0, slots=0), [])
        # number == 1 returns [[1]]
        self.assertEqual(get_partitions_simple_recursion(number=1, slots=1), [[1]])

    def test_num_prime_integer_partitions_examples_and_edges(self):
        # Examples adjusted to actual implementation behavior
        # There are 5 prime partitions of 10: [2,2,2,2,2], [3,3,2,2], [5,3,2], [5,5], [7,3]
        self.assertEqual(num_prime_partitions_simple_recursion(number=10, slots=10), 5)
        # With slots=5, primes greater than 5 are excluded; valid: [2,2,2,2,2], [3,3,2,2], [5,3,2], [5,5]
        self.assertEqual(num_prime_partitions_simple_recursion(number=10, slots=5), 4)
        # Additional small checks
        self.assertEqual(num_prime_partitions_simple_recursion(number=5, slots=5), 2)  # [2,3], [5]
        # Edges
        self.assertEqual(num_prime_partitions_simple_recursion(number=0, slots=10), 1)
        self.assertEqual(num_prime_partitions_simple_recursion(number=10, slots=1), 0)
        with self.assertRaises(IntegerPartitionError) as cm:
            num_prime_partitions_simple_recursion(number=-1, slots=10)
        self.assertEqual(str(cm.exception), 'number and slots must be non-negative')

    def test_get_prime_partitions_examples_and_boundaries(self):
        # Exact lists as produced by implementation (non-increasing sequences)
        self.assertEqual(
                get_prime_partitions_simple_recursion(number=10, slots=10),
                [[2, 2, 2, 2, 2], [3, 3, 2, 2], [5, 3, 2], [5, 5], [7, 3]],
        )
        self.assertEqual(
                get_prime_partitions_simple_recursion(number=10, slots=5),
                [[2, 2, 2, 2, 2], [3, 3, 2, 2], [5, 3, 2], [5, 5]],
        )
        # Boundaries
        self.assertEqual(get_prime_partitions_simple_recursion(number=1, slots=10), [])
        self.assertEqual(get_prime_partitions_simple_recursion(number=10, slots=1), [])

    def test_get_prime_partitions_errors(self):
        # Overflow error with exact message
        with self.assertRaises(OverflowError) as cm:
            get_prime_partitions_simple_recursion(number=6, slots=6, safe_limit=5)
        self.assertEqual(str(cm.exception), 'number must be less than safe_limit=5')

        # Negative error
        with self.assertRaises(IntegerPartitionError) as cm:
            get_prime_partitions_simple_recursion(number=-2, slots=5)
        self.assertEqual(str(cm.exception), 'number and slots must be non-negative')

    def test_main(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
