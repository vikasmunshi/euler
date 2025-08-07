#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for the Prime Number Utilities Module

This module contains unit tests for the prime number generation and analysis
functions defined in euler.utils.primes.
"""

import unittest

from euler.logger import logger
from euler.maths.primes import (PrimeError, _CACHE, ensure_prime_cache_is_loaded, euler_totient,
                                gen_primes_sieve_eratosthenes, get_divisors, get_max_cached_primes,
                                get_pre_computed_primes_sundaram_sieve, get_relative_primes, is_prime,
                                prime_factor_count, prime_factorization, proper_factors, seed_cache)

# Set logger level to ERROR to suppress informational messages during tests
logger.setLevel('ERROR')


class TestPrimeNumberCache(unittest.TestCase):
    def setUp(self):
        _CACHE['primes'] = tuple()
        _CACHE['primes_set'] = set()
        _CACHE['max_limit'] = 0

    def tearDown(self):
        _CACHE['primes'] = tuple()
        _CACHE['primes_set'] = set()
        _CACHE['max_limit'] = 0

    def test_ensure_prime_cache_is_loaded_decorator(self):
        """Test that the ensure_prime_cache_is_loaded decorator loads primes cache."""

        # Define a test function with the decorator
        @ensure_prime_cache_is_loaded
        def test_function():
            return get_max_cached_primes() > 0

        # The cache should be loaded during function definition
        self.assertTrue(get_max_cached_primes() > 0)

        # The function should work as expected
        self.assertTrue(test_function())

    def test_seed_cache(self):
        """Test seed_cache function."""
        seed_cache(regenerate=False)
        max_limit = get_max_cached_primes()
        self.assertTrue(max_limit > 0)
        seed_cache(regenerate=True)
        max_limit_regenerated = get_max_cached_primes()
        self.assertTrue(max_limit_regenerated > 0)
        self.assertEqual(max_limit, max_limit_regenerated)


class TestPrimeIsPrime(unittest.TestCase):
    def setUp(self):
        _CACHE['primes'] = tuple()
        _CACHE['primes_set'] = set()
        _CACHE['max_limit'] = 0

    def tearDown(self):
        _CACHE['primes'] = tuple()
        _CACHE['primes_set'] = set()
        _CACHE['max_limit'] = 0

    def test_is_prime_with_primes_sieve(self):
        """Test is_prime function with primes sieve."""
        max_limit = 100
        results = [n for n in range(max_limit) if is_prime(n)]
        expected_primes = list(get_pre_computed_primes_sundaram_sieve(max_limit=max_limit))
        self.assertEqual(results, expected_primes)


class TestPrimeNumberUtilities(unittest.TestCase):
    def test_is_prime_small_numbers(self):
        """Test is_prime function with small numbers."""
        # Test known primes
        self.assertTrue(is_prime(2))  # Smallest prime
        self.assertTrue(is_prime(3))
        self.assertTrue(is_prime(5))
        self.assertTrue(is_prime(7))
        self.assertTrue(is_prime(11))
        self.assertTrue(is_prime(13))
        self.assertTrue(is_prime(17))
        self.assertTrue(is_prime(19))
        self.assertTrue(is_prime(23))

        # Test known non-primes
        self.assertFalse(is_prime(1))  # 1 is not prime by definition
        self.assertFalse(is_prime(4))  # 2×2
        self.assertFalse(is_prime(6))  # 2×3
        self.assertFalse(is_prime(8))  # 2×4
        self.assertFalse(is_prime(9))  # 3×3
        self.assertFalse(is_prime(10))  # 2×5
        self.assertFalse(is_prime(12))  # 2×6
        self.assertFalse(is_prime(15))  # 3×5

    def test_is_prime_larger_numbers(self):
        """Test is_prime function with larger numbers."""
        # Test larger known primes
        self.assertTrue(is_prime(97))  # Last two-digit prime
        self.assertTrue(is_prime(101))  # First three-digit prime
        self.assertTrue(is_prime(997))  # Largest 3-digit prime
        self.assertTrue(is_prime(7919))  # 1000th prime

        # Test larger known non-primes
        self.assertFalse(is_prime(100))  # 2×2×5×5
        self.assertFalse(is_prime(999))  # 3×3×3×37
        self.assertFalse(is_prime(1001))  # 7×11×13

        # Test with large prime numbers from primes.txt
        self.assertTrue(is_prime(99901))  # A large prime from primes.txt
        self.assertTrue(is_prime(99971))  # A large prime from primes.txt
        self.assertTrue(is_prime(99989))  # A large prime from primes.txt
        self.assertTrue(is_prime(99991))  # A large prime from primes.txt
        self.assertTrue(is_prime(99999989))  # A large prime number

    def test_sundaram_sieve(self):
        """Test gen_primes_sundaram_sieve function."""
        # Test with different limits
        self.assertEqual(get_pre_computed_primes_sundaram_sieve(max_limit=2), (2,))
        self.assertEqual(get_pre_computed_primes_sundaram_sieve(max_limit=3), (2, 3))
        self.assertEqual(get_pre_computed_primes_sundaram_sieve(max_limit=10), (2, 3, 5, 7))
        self.assertEqual(get_pre_computed_primes_sundaram_sieve(max_limit=20), (2, 3, 5, 7, 11, 13, 17, 19))

        # Check a specific larger range
        primes_to_50 = get_pre_computed_primes_sundaram_sieve(max_limit=50)
        expected_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)
        self.assertEqual(primes_to_50, expected_primes)

        # Test with large primes
        large_primes = get_pre_computed_primes_sundaram_sieve(max_limit=100000)
        # Check if specific large primes are included in the generated list
        expected_last_four = (99961, 99971, 99989, 99991)
        self.assertEqual(large_primes[-4:], expected_last_four)

    def test_prime_sieve_generator(self):
        """Test gen_primes_sieve generator function."""
        # Generate first 15 primes
        prime_gen = gen_primes_sieve_eratosthenes()
        first_15_primes = [next(prime_gen) for _ in range(15)]
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        self.assertEqual(first_15_primes, expected_primes)
        # Test with large primes
        prime_gen = gen_primes_sieve_eratosthenes()
        large_primes = [next(prime_gen) for _ in range(9999)]
        # Check if specific large primes are included in the generated list
        expected_last_four = [104707, 104711, 104717, 104723]
        self.assertEqual(large_primes[-4:], expected_last_four)

    def test_prime_factorization(self):
        """Test prime_factorization function."""
        for not_prime in (-1, 0, 1):
            with self.assertRaises(PrimeError):
                prime_factorization(not_prime)
        # Test with prime numbers (should return just the number itself with exponent 1)
        self.assertEqual(prime_factorization(2), ((2, 1),))
        self.assertEqual(prime_factorization(3), ((3, 1),))
        self.assertEqual(prime_factorization(7), ((7, 1),))
        self.assertEqual(prime_factorization(13), ((13, 1),))

        # Test with composite numbers
        self.assertEqual(prime_factorization(4), ((2, 2),))  # 2²
        self.assertEqual(prime_factorization(6), ((2, 1), (3, 1)))  # 2×3
        self.assertEqual(prime_factorization(8), ((2, 3),))  # 2³
        self.assertEqual(prime_factorization(12), ((2, 2), (3, 1)))  # 2²×3
        self.assertEqual(prime_factorization(60), ((2, 2), (3, 1), (5, 1)))  # 2²×3×5
        self.assertEqual(prime_factorization(100), ((2, 2), (5, 2)))  # 2²×5²

        # Test with larger numbers
        self.assertEqual(prime_factorization(720), ((2, 4), (3, 2), (5, 1)))  # 2⁴×3²×5
        self.assertEqual(prime_factorization(997), ((997, 1),))  # Prime
        self.assertEqual(prime_factorization(999), ((3, 3), (37, 1)))  # 3³×37

        # Test with large prime numbers from primes.txt
        self.assertEqual(prime_factorization(99901), ((99901, 1),))  # Large prime
        self.assertEqual(prime_factorization(99971 * 99989), ((99971, 1), (99989, 1)))  # Product of two large primes

    def test_get_divisors(self):
        """Test get_divisors function."""
        # Test with small numbers
        self.assertEqual(get_divisors(2), (1, 2))
        self.assertEqual(get_divisors(3), (1, 3))
        self.assertEqual(get_divisors(4), (1, 2, 4))
        self.assertEqual(get_divisors(6), (1, 2, 3, 6))
        self.assertEqual(get_divisors(12), (1, 2, 3, 4, 6, 12))

        # Test with perfect numbers
        self.assertEqual(get_divisors(6), (1, 2, 3, 6))  # First perfect number
        self.assertEqual(get_divisors(28), (1, 2, 4, 7, 14, 28))  # Second perfect number

        # Test with prime numbers
        self.assertEqual(get_divisors(7), (1, 7))
        self.assertEqual(get_divisors(13), (1, 13))
        self.assertEqual(get_divisors(19), (1, 19))

        # Test with larger composite numbers
        self.assertEqual(get_divisors(100), (1, 2, 4, 5, 10, 20, 25, 50, 100))  # 2²×5²
        self.assertEqual(get_divisors(144), (1, 2, 3, 4, 6, 8, 9, 12, 16, 18, 24, 36, 48, 72, 144))  # 2⁴×3²

        # Test with special cases
        self.assertEqual(get_divisors(1), (1,))  # 1 has only itself as a divisor

        divisors_of_496 = get_divisors(496)  # Third perfect number: 496 = 2⁴×31
        self.assertEqual(sum(divisors_of_496[:-1]), 496)  # Sum of proper divisors equals the number

    def test_proper_factors(self):
        """Test proper_factors function."""
        # Test with small numbers
        # Note: n=1 is not valid for proper_factors as it requires n > 1
        self.assertEqual(proper_factors(2), (1,))
        self.assertEqual(proper_factors(4), (1, 2))
        self.assertEqual(proper_factors(6), (1, 2, 3))
        self.assertEqual(proper_factors(12), (1, 2, 3, 4, 6))

        # Test with perfect numbers
        self.assertEqual(proper_factors(6), (1, 2, 3))  # Sum = 6
        self.assertEqual(proper_factors(28), (1, 2, 4, 7, 14))  # Sum = 28
        self.assertEqual(sum(proper_factors(496)), 496)  # Third perfect number

        # Test with prime numbers
        self.assertEqual(proper_factors(7), (1,))
        self.assertEqual(proper_factors(13), (1,))
        self.assertEqual(proper_factors(19), (1,))

        # Test with abundant numbers (sum of proper divisors > number)
        self.assertEqual(sum(proper_factors(12)), 16)  # 12 < 16
        self.assertEqual(sum(proper_factors(18)), 21)  # 18 < 21
        self.assertEqual(sum(proper_factors(20)), 22)  # 20 < 22

        # Test with deficient numbers (sum of proper divisors < number)
        self.assertEqual(sum(proper_factors(10)), 8)  # 10 > 8
        self.assertEqual(sum(proper_factors(14)), 10)  # 14 > 10
        self.assertEqual(sum(proper_factors(21)), 11)  # 21 > 11

    def test_proper_factors_validation(self):
        """Test proper_factors function validates input correctly."""
        # Test that proper_factors raises ValueError for n=1
        with self.assertRaises(ValueError) as context:
            proper_factors(1)
        self.assertTrue('n must be greater than 1' in str(context.exception))

    def test_get_divisors_validation(self):
        """Test get_divisors function validates input correctly."""
        # Test that get_divisors raises PrimeError for n=0
        with self.assertRaises(PrimeError) as context:
            get_divisors(0)
        self.assertTrue('n must be greater than 0' in str(context.exception))

        # Test that get_divisors raises PrimeError for negative numbers
        with self.assertRaises(PrimeError) as context:
            get_divisors(-5)
        self.assertTrue('n must be greater than 0' in str(context.exception) or
                        'n must be positive' in str(context.exception))

    def test_prime_factor_count(self):
        """Test prime_factor_count function."""
        # Test with small numbers
        self.assertEqual(prime_factor_count(1), 0)  # 1 has no prime factors
        self.assertEqual(prime_factor_count(2), 1)  # Prime
        self.assertEqual(prime_factor_count(4), 1)  # Only factor is 2
        self.assertEqual(prime_factor_count(6), 2)  # Factors: 2, 3
        self.assertEqual(prime_factor_count(12), 2)  # Factors: 2, 3
        self.assertEqual(prime_factor_count(30), 3)  # Factors: 2, 3, 5

        # Test with numbers having repeated prime factors
        self.assertEqual(prime_factor_count(8), 1)  # Only factor is 2
        self.assertEqual(prime_factor_count(9), 1)  # Only factor is 3
        self.assertEqual(prime_factor_count(18), 2)  # Factors: 2, 3

        # Test with larger numbers
        self.assertEqual(prime_factor_count(210), 4)  # 2×3×5×7
        self.assertEqual(prime_factor_count(2310), 5)  # 2×3×5×7×11
        self.assertEqual(prime_factor_count(2520), 4)  # 2³×3²×5×7

        # Test with large prime numbers
        self.assertEqual(prime_factor_count(99901), 1)  # Large prime
        # Test with products of large primes
        self.assertEqual(prime_factor_count(99901 * 99991), 2)  # Product of two large primes

    def test_get_relative_primes(self):
        """Test get_relative_primes function."""
        # Test with small numbers
        self.assertEqual(get_relative_primes(2), (1,))
        self.assertEqual(get_relative_primes(3), (1, 2))
        self.assertEqual(get_relative_primes(4), (1, 3))
        self.assertEqual(get_relative_primes(6), (1, 5))

        # Test with prime numbers (all numbers less than n are coprime to n)
        self.assertEqual(get_relative_primes(7), (1, 2, 3, 4, 5, 6))
        self.assertEqual(get_relative_primes(11), tuple(range(1, 11)))

        # Test with larger composite numbers
        self.assertEqual(get_relative_primes(8), (1, 3, 5, 7))
        self.assertEqual(get_relative_primes(9), (1, 2, 4, 5, 7, 8))
        self.assertEqual(get_relative_primes(10), (1, 3, 7, 9))

        # Verify the number of relative primes equals euler_totient
        for n in range(2, 20):
            self.assertEqual(len(get_relative_primes(n)), euler_totient(n))

    def test_euler_totient(self):
        """Test euler_totient function."""
        # Test with small numbers
        self.assertEqual(euler_totient(1), 1)
        self.assertEqual(euler_totient(2), 1)
        self.assertEqual(euler_totient(3), 2)
        self.assertEqual(euler_totient(4), 2)
        self.assertEqual(euler_totient(5), 4)
        self.assertEqual(euler_totient(6), 2)
        self.assertEqual(euler_totient(7), 6)
        self.assertEqual(euler_totient(8), 4)
        self.assertEqual(euler_totient(9), 6)
        self.assertEqual(euler_totient(10), 4)

        # Test with larger numbers
        self.assertEqual(euler_totient(12), 4)
        self.assertEqual(euler_totient(30), 8)
        self.assertEqual(euler_totient(36), 12)

        # Test with prime powers
        self.assertEqual(euler_totient(16), 8)  # 2⁴
        self.assertEqual(euler_totient(27), 18)  # 3³
        self.assertEqual(euler_totient(32), 16)  # 2⁵

        # Test with prime numbers
        self.assertEqual(euler_totient(11), 10)
        self.assertEqual(euler_totient(13), 12)
        self.assertEqual(euler_totient(17), 16)
        self.assertEqual(euler_totient(19), 18)

        # Test with larger numbers
        self.assertEqual(euler_totient(60), 16)  # 2² × 3 × 5
        self.assertEqual(euler_totient(100), 40)  # 2² × 5²

        # Test mathematical properties
        # For prime p, φ(p) = p-1
        self.assertEqual(euler_totient(23), 22)
        self.assertEqual(euler_totient(97), 96)

        # For coprime m and n, φ(m×n) = φ(m) × φ(n)
        self.assertEqual(euler_totient(15), euler_totient(3) * euler_totient(5))  # 3 and 5 are coprime
        self.assertEqual(euler_totient(77), euler_totient(7) * euler_totient(11))  # 7 and 11 are coprime

        # For prime p and k>0, φ(p^k) = p^k - p^(k-1)
        self.assertEqual(euler_totient(8), 8 - 4)  # 2³ - 2²
        self.assertEqual(euler_totient(27), 27 - 9)  # 3³ - 3²

        # Test with large prime
        self.assertEqual(euler_totient(99901), 99900)  # φ(prime) = prime-1

        # Test with products of multiple large primes and a small prime
        large_product = 99901 * 99989 * 3  # Product of two large primes and a small prime
        expected_totient = 99900 * 99988 * 2  # φ(p₁p₂p₃) = φ(p₁)φ(p₂)φ(p₃) for distinct primes
        self.assertEqual(euler_totient(large_product), expected_totient)

        # Test another combination with large and small primes
        another_product = 99971 * 99991 * 7  # Another product of two large primes and a small prime
        another_expected = 99970 * 99990 * 6  # φ(p₁p₂p₃) = φ(p₁)φ(p₂)φ(p₃)
        self.assertEqual(euler_totient(another_product), another_expected)


if __name__ == '__main__':
    unittest.main()
