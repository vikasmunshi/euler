#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prime Number Generation and Number Theory Module

This module provides a comprehensive set of functions for generating and working with prime numbers
and performing number theory operations, primarily to support Project Euler problem solutions that
require efficient mathematical algorithms.

Key functionality includes:
- Prime number generation with the Sundaram sieve algorithm
- Primality testing with optimized trial division
- Prime factorization of integers
- Divisor enumeration (both proper and improper)
- Counting unique prime factors

Performance optimizations:
- Caching strategies improve performance for repeated operations
- Pre-computed cache of primes up to 100 for immediate access
- Function-level memoization with lru_cache decorator
- Wheel factorization technique to skip non-candidate numbers
- Strategic use of mathematical properties to minimize computation

Mathematical principles used:
- Sundaram sieve for efficient prime generation
- Trial division limited to sqrt(n) for primality testing
- Prime factorization based on fundamental theorem of arithmetic
- Wheel factorization patterns to optimize trial division

These utilities form the foundation for solving many Project Euler problems that
involve number theory concepts and prime number manipulation.
"""
from collections import namedtuple
from functools import lru_cache
from itertools import takewhile
from typing import Tuple, Set

# Pre-computed cache of prime numbers up to 100 for quick access
# This improves performance for small prime number requests
_PRIME_CACHE: Tuple[int, ...] = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
                                 89, 97)
# Tracks the current maximum limit of the prime cache
_MAX_LIMIT: int = 100


def gen_primes_sundaram_sieve(*, max_limit: int) -> Tuple[int, ...]:
    """
    Generate prime numbers up to max_limit using the Sundaram sieve algorithm.

    The Sundaram sieve is an efficient algorithm for finding all prime numbers up to a specified limit.
    It works by eliminating numbers of the form i+j+2ij where i,j are positive integers.
    The remaining numbers are mapped to primes through the formula 2n+1.

    This function uses a caching mechanism to avoid recalculating primes that have already been generated.
    When a larger max_limit is requested than the previous calls, the cache is extended to include
    additional primes up to the new limit.

    Args:
        max_limit: The upper limit for generating prime numbers

    Returns:
        A tuple containing all prime numbers up to max_limit

    Examples:
        >>> gen_primes_sundaram_sieve(10)
        (2, 3, 5, 7)
        >>> gen_primes_sundaram_sieve(20)
        (2, 3, 5, 7, 11, 13, 17, 19)
        >>> gen_primes_sundaram_sieve(5)
        (2, 3, 5)
    """
    global _PRIME_CACHE, _MAX_LIMIT
    if max_limit > _MAX_LIMIT:
        # Calculate the upper bound for the sieve
        max_number = (max_limit - 1) // 2 + 1

        # Initialize an array of candidate numbers
        numbers = list(range(0, max_number))

        # Apply the Sundaram sieve algorithm
        for i in range(1, max_number):
            for j in range(i, max_number):
                index = i + j + (2 * i * j)
                if index < max_number:
                    # Mark n where 2n+1 is not prime as 0
                    numbers[index] = 0
                else:
                    # Break the inner loop when we exceed the array bounds
                    break

        # Generate the final sequence of primes
        # Include 2 (the only even prime) and all odd primes
        # Filter to ensure we only return primes up to max_limit
        _PRIME_CACHE, _MAX_LIMIT = (2,) + tuple(2 * n + 1 for n in numbers[1:] if n != 0), max_limit
    return tuple(takewhile(lambda p: p <= max_limit, _PRIME_CACHE))


@lru_cache()
def is_prime(n: int) -> bool:
    """
    Determine whether a number is prime.

    This function tests if a given number is prime by checking if it's divisible
    by any integer from 2 to the square root of the number.

    Args:
        n: The number to test for primality

    Returns:
        True if the number is prime, False otherwise

    Examples:
        >>> is_prime(2)
        True
        >>> is_prime(17)
        True
        >>> is_prime(20)
        False
    """
    # Handle edge cases
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Check divisibility by odd numbers up to sqrt(n)
    for i in gen_primes_sundaram_sieve(max_limit=int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


Factor = namedtuple('Factor', ['base', 'exponent'])


@lru_cache()
def prime_factorization(n: int) -> Tuple[Factor, ...]:
    """
    Factorizes a number into its prime factors.

    Args:
        n: The integer to be factorized (n > 1).

    Returns:
        A tuple of Factors, where each Factor contains:
        - base: The prime factor
        - exponent: How many times the factor divides n

    Example:
        >>> prime_factorization(28)
        (Factor(base=2, exponent=2), Factor(base=7, exponent=1))
    """
    factors = []

    for prime in gen_primes_sundaram_sieve(max_limit=int(n ** 0.5) + 1):  # Iterate over primes up to sqrt(n)
        if prime > n:
            break

        exponent = 0
        while n % prime == 0:  # Count the power of this prime
            n //= prime
            exponent += 1

        if exponent > 0:
            factors.append(Factor(base=prime, exponent=exponent))

    if n > 1:  # If n is still greater than 1, it is a prime factor
        factors.append(Factor(base=n, exponent=1))

    return tuple(factors)


@lru_cache()
def divisors(n: int) -> Tuple[int, ...]:
    """
    Computes the divisors of a number `n` (including `n` itself).

    Args:
        n: The integer to compute proper factors for (n > 0).

    Returns:
        A list of integers representing all divisors of `n`.

    Example:
        >>> divisors(12)
        [1, 2, 3, 4, 6, 12]
    """
    if n < 1:
        raise ValueError(f'n must be greater than 1 (got n={n}')
    factors: Set[int] = {1}
    for base, exponent in prime_factorization(n):
        factors.update({f * (base ** power) for power in range(1, exponent + 1) for f in factors})
    return tuple(sorted(factors))


@lru_cache()
def proper_factors(n: int) -> Tuple[int, ...]:
    """
    Computes the proper factors of a number `n` (excluding `n` itself).

    Args:
        n: The integer to compute proper factors for (n > 0).

    Returns:
        A list of integers representing all proper factors of `n`.

    Example:
        >>> proper_factors(12)
        [1, 2, 3, 4, 6]
    """
    return divisors(n)[:-1]


@lru_cache()
def prime_factor_count(num: int) -> int:
    """
    Count the number of unique prime factors of a positive integer.

    This function determines the number of distinct prime factors of an integer using
    an optimized wheel factorization approach. Instead of testing divisibility by all
    integers, it uses a pattern of gaps between potential prime factors to improve
    efficiency.

    The wheel pattern is:
    - For factors < 11: Use gaps [1, 1, 2, 2, 4] (checking 2, 3, 5, 7, 11...)
    - For factors ≥ 11: Use gaps [2, 4, 2, 4, 6, 2, 6, 4] (a pattern that skips
      multiples of 2, 3, 5, reducing the number of divisibility tests)

    Each unique prime factor is counted only once, regardless of its multiplicity.
    For example, 12 = 2² × 3 has 2 unique prime factors (2 and 3).

    Args:
        num: A positive integer to factorize

    Returns:
        The number of unique prime factors of num

    Examples:
        >>> prime_factor_count(12)  # 12 = 2² × 3
        2
        >>> prime_factor_count(14)  # 14 = 2 × 7
        2
        >>> prime_factor_count(17)  # 17 is prime
        1
        >>> prime_factor_count(60)  # 60 = 2² × 3 × 5
        3
    """
    factor, num_factors = 1, 0
    while factor <= int(num ** 0.5):
        for gap in ([1, 1, 2, 2, 4] if factor < 11 else [2, 4, 2, 4, 6, 2, 6, 4]):
            factor, is_new_factor = factor + gap, True
            while num % factor == 0:
                num //= factor
                if is_new_factor:
                    num_factors, is_new_factor = num_factors + 1, False
    # If num is still > 1, it means num itself is a prime factor
    # that we couldn't find divisors for during the trial division
    return num_factors + (0 if num == 1 else 1)
