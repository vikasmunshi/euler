#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the integer_partitions module."""

import unittest

from euler.maths.integer_partitions import (IntegerPartitionError, get_partitions, get_prime_partitions, main,
                                            num_integer_partitions, num_partitions, num_prime_integer_partitions)


class TestIntegerPartitions(unittest.TestCase):
    """Test case for integer_partitions.py utility functions."""

    def test_main_function(self):
        """Test that the main function returns 0."""
        self.assertEqual(main(), 0)

    def test_basic_partitions(self):
        """Test basic partition cases."""
        # Test partitions of 1
        self.assertEqual(get_partitions(number=1, slots=1), [[1]])

        # Test partitions of 2
        partitions_2 = get_partitions(number=2, slots=2)
        self.assertEqual(len(partitions_2), 2)
        self.assertIn([1, 1], partitions_2)
        self.assertIn([2], partitions_2)

        # Test partitions of 3
        partitions_3 = get_partitions(number=3, slots=3)
        self.assertEqual(len(partitions_3), 3)
        self.assertIn([1, 1, 1], partitions_3)
        self.assertIn([2, 1], partitions_3)
        self.assertIn([3], partitions_3)

        # Test partitions of 4
        partitions_4 = get_partitions(number=4, slots=4)
        self.assertEqual(len(partitions_4), 5)
        self.assertIn([1, 1, 1, 1], partitions_4)
        self.assertIn([2, 1, 1], partitions_4)
        self.assertIn([2, 2], partitions_4)
        self.assertIn([3, 1], partitions_4)
        self.assertIn([4], partitions_4)

    def test_partitions_with_slots_constraint(self):
        """Test partitions with slot constraints."""
        # Test partitions of 4 with max slot of 2
        partitions_4_2 = get_partitions(number=4, slots=2)
        self.assertEqual(len(partitions_4_2), 3)
        self.assertIn([1, 1, 1, 1], partitions_4_2)
        self.assertIn([2, 1, 1], partitions_4_2)
        self.assertIn([2, 2], partitions_4_2)
        self.assertNotIn([3, 1], partitions_4_2)
        self.assertNotIn([4], partitions_4_2)

        # Test partitions of 5 with max slot of 3
        partitions_5_3 = get_partitions(number=5, slots=3)
        self.assertEqual(len(partitions_5_3), 5)
        self.assertIn([1, 1, 1, 1, 1], partitions_5_3)
        self.assertIn([2, 1, 1, 1], partitions_5_3)
        self.assertIn([2, 2, 1], partitions_5_3)
        self.assertIn([3, 1, 1], partitions_5_3)
        self.assertIn([3, 2], partitions_5_3)
        self.assertNotIn([4, 1], partitions_5_3)
        self.assertNotIn([5], partitions_5_3)

        # Test partitions of 6 with max slot of 2
        partitions_6_2 = get_partitions(number=6, slots=2)
        self.assertEqual(len(partitions_6_2), 4)
        self.assertIn([1, 1, 1, 1, 1, 1], partitions_6_2)
        self.assertIn([2, 1, 1, 1, 1], partitions_6_2)
        self.assertIn([2, 2, 1, 1], partitions_6_2)
        self.assertIn([2, 2, 2], partitions_6_2)

    def test_larger_partitions(self):
        """Test with slightly larger numbers."""
        # Test partitions of 7 with max slot of 7
        partitions_7 = get_partitions(number=7, slots=7)
        self.assertEqual(len(partitions_7), 15)  # Known number of partitions for 7

        # Test partitions of 10 with max slot of 5
        partitions_10_5 = get_partitions(number=10, slots=5)
        # Number of partitions of 10 with max part 5 should be 30
        self.assertEqual(len(partitions_10_5), 30)

        # Test specific partitions of 10
        self.assertIn([5, 5], partitions_10_5)
        self.assertIn([5, 3, 2], partitions_10_5)
        self.assertIn([5, 4, 1], partitions_10_5)
        self.assertIn([5, 3, 1, 1], partitions_10_5)
        self.assertIn([5, 2, 2, 1], partitions_10_5)
        self.assertIn([5, 2, 1, 1, 1], partitions_10_5)
        self.assertIn([5, 1, 1, 1, 1, 1], partitions_10_5)
        self.assertIn([4, 4, 2], partitions_10_5)
        self.assertIn([4, 4, 1, 1], partitions_10_5)
        self.assertNotIn([6, 4], partitions_10_5)  # 6 exceeds max slot of 5
        self.assertNotIn([10], partitions_10_5)  # 10 exceeds max slot of 5

    def test_validation(self):
        """Test input validation."""
        # Test negative number
        with self.assertRaises(IntegerPartitionError):
            get_partitions(number=-1, slots=5)

        # Test negative slots
        with self.assertRaises(IntegerPartitionError):
            get_partitions(number=5, slots=-2)

        # Test number < slots
        with self.assertRaises(IntegerPartitionError):
            get_partitions(number=3, slots=5)

        # Test safe limit
        with self.assertRaises(OverflowError):
            get_partitions(number=100, slots=10, safe_limit=50)

        # Test validation in num_integer_partitions
        with self.assertRaises(IntegerPartitionError):
            num_integer_partitions(number=-1, slots=5)

        with self.assertRaises(IntegerPartitionError):
            num_integer_partitions(number=5, slots=-1)

        with self.assertRaises(IntegerPartitionError):
            num_integer_partitions(number=3, slots=5)

        # Test validation in num_prime_integer_partitions
        with self.assertRaises(IntegerPartitionError):
            num_prime_integer_partitions(number=-1, slots=5)

        with self.assertRaises(IntegerPartitionError):
            num_prime_integer_partitions(number=5, slots=-1)

        # Test validation in get_prime_partitions
        with self.assertRaises(OverflowError):
            get_prime_partitions(number=100, slots=10, safe_limit=50)

        with self.assertRaises(IntegerPartitionError):
            get_prime_partitions(number=-1, slots=5)

        with self.assertRaises(IntegerPartitionError):
            get_prime_partitions(number=5, slots=-1)

    def test_special_cases(self):
        """Test special edge cases."""
        # Test with number=0
        self.assertEqual(get_partitions(number=0, slots=0), [])

        # Test with exactly matching constraints
        self.assertEqual(get_partitions(number=5, slots=5), get_partitions(number=5, slots=5, safe_limit=10))

        # Test num_partitions with 0
        self.assertEqual(num_partitions(0), 1)

        # Test num_partitions with negative number
        self.assertEqual(num_partitions(-5), 0)

        # Test num_integer_partitions with 0 and 1
        self.assertEqual(num_integer_partitions(number=0, slots=0), 0)
        self.assertEqual(num_integer_partitions(number=1, slots=1), 1)

        # Test num_prime_integer_partitions with 0
        self.assertEqual(num_prime_integer_partitions(number=0, slots=5), 1)

        # Test num_prime_integer_partitions with small slots
        self.assertEqual(num_prime_integer_partitions(number=5, slots=1), 0)

        # Test get_prime_partitions with small values
        self.assertEqual(get_prime_partitions(number=1, slots=10), [])
        self.assertEqual(get_prime_partitions(number=5, slots=1), [])

        # Test number=slots (should only have one partition)
        partitions_equal = get_partitions(number=5, slots=5)
        self.assertIn([5], partitions_equal)

        # Test with custom safe_limit
        partitions_20_10 = get_partitions(number=20, slots=10, safe_limit=30)
        self.assertGreater(len(partitions_20_10), 100)  # Should have many partitions

    def test_partition_sum_verification(self):
        """Verify that all partitions sum to the expected number."""
        # Check that each partition sums to the number
        for n in range(1, 8):
            partitions = get_partitions(number=n, slots=n)
            for partition in partitions:
                self.assertEqual(sum(partition), n, f"Partition {partition} of {n} sums to {sum(partition)}")

    def test_partition_ordering(self):
        """Test that partitions maintain a specific ordering property."""
        # In each partition, elements should be in non-increasing order
        partitions_8 = get_partitions(number=8, slots=8)
        for partition in partitions_8:
            # Check that each element is greater than or equal to the next
            for i in range(len(partition) - 1):
                self.assertGreaterEqual(partition[i], partition[i + 1],
                                        f"Partition {partition} is not in non-increasing order")


if __name__ == '__main__':
    unittest.main()
