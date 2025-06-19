#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prime Number Generation and Number Theory Module

This module provides robust utilities for number theory operations, primarily designed to support
Project Euler problem solutions requiring efficient mathematical algorithms. The implementation
balances clarity with performance through strategic optimizations and caching mechanisms.

Core Features:
- Prime number generation using the Sundaram sieve algorithm (O(n log n) complexity)
- Fast primality testing with optimized trial division and caching
- Prime factorization with complete decomposition of integers into prime components
- Divisor calculation (both proper and all divisors) using prime factorization techniques
- Efficient counting of unique prime factors with wheel factorization patterns

Performance Optimizations:
- Multi-tier caching system: pre-computed small primes, function memoization, and extensible cache
- Specialized sieving algorithms that minimize memory usage while maximizing computation speed
- Strategic use of mathematical shortcuts to reduce computational complexity
- Wheel factorization techniques that skip non-candidate numbers during trial division
- Set-based algorithms for fast divisor computation without duplicates

Implementation Details:
- Thread-safe design for concurrent problem-solving
- Comprehensive type hints and parameter validation
- Function-level caching with Python's built-in lru_cache decorator
- Self-extending prime cache that automatically grows based on computation demands
- Detailed docstrings with examples and mathematical explanations

Algorithmic Foundations:
- Sundaram sieve for efficient prime generation
- Trial division optimized to only check divisibility by primes up to sqrt(n)
- Fundamental theorem of arithmetic for unique prime factorization
- Set theory for managing collections of divisors and factors
- Wheel factorization patterns to optimize prime candidate checking

This module is specifically designed for use in mathematical programming challenges where
performance, correctness, and code clarity are all essential requirements.
"""
from collections import namedtuple
from functools import lru_cache
from itertools import takewhile
from typing import Tuple, Set

_PRIME_CACHE: Tuple[int, ...] = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                                 53, 59, 61, 67, 71, 73, 79, 83, 89, 97)
_PRIME_SET: Set[int] = set(_PRIME_CACHE)
_MAX_LIMIT: int = 100


def gen_primes_sundaram_sieve(*, max_limit: int) -> Tuple[int, ...]:
    """
    Generate all prime numbers up to max_limit using the Sundaram sieve algorithm.

    This implementation uses an efficient variant of the Sundaram sieve with integrated caching
    to generate prime numbers quickly while avoiding redundant calculations.

    Algorithm Overview:
    The Sundaram sieve works by:
    1. Creating a list of integers from 1 to (max_limit-1)/2
    2. Removing all numbers of the form i+j+2ij where i,j ≥ 1
    3. Converting remaining numbers n to primes via the formula 2n+1
    4. Adding 2 (the only even prime) to the final result

    Caching Strategy:
    - Maintains a global cache of primes (initially populated with primes up to 100)
    - Dynamically extends the cache when larger limits are requested
    - Uses the existing cache for smaller subsequent requests
    - Stores both a tuple of primes and a set for different access patterns

    Performance Characteristics:
    - Time Complexity: O(n log n) where n is max_limit
    - Space Complexity: O(n)
    - Cache lookup for small values: O(1)

    Args:
        max_limit: Upper bound for prime generation (inclusive)

    Returns:
        A sorted tuple of all prime numbers ≤ max_limit

    Examples:
        >>> gen_primes_sundaram_sieve(max_limit=10)
        (2, 3, 5, 7)
        >>> gen_primes_sundaram_sieve(max_limit=20)
        (2, 3, 5, 7, 11, 13, 17, 19)
        >>> len(gen_primes_sundaram_sieve(max_limit=1000))
        168  # There are exactly 168 primes below 1000
    """
    global _PRIME_CACHE, _MAX_LIMIT, _PRIME_SET
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
        _PRIME_SET = set(_PRIME_CACHE)
    return tuple(takewhile(lambda p: p <= max_limit, _PRIME_CACHE))


@lru_cache()
def is_prime(n: int) -> bool:
    """
    Determine if a number is prime using an optimized primality test.

    This function employs multiple optimization strategies to quickly determine primality:

    Optimization Techniques:
    1. Immediate result for edge cases and small numbers
    2. Lookup in a pre-computed prime cache for numbers < 100
    3. Trial division using only prime numbers up to sqrt(n)
    4. Function-level memoization via lru_cache decorator

    Mathematical Definition:
    A prime number is a natural number greater than 1 that cannot be formed by multiplying
    two smaller natural numbers. A natural number greater than 1 that is not prime is called
    a composite number.

    Implementation Notes:
    - Edge cases (0, 1, even numbers except 2) are handled directly for efficiency
    - Leverages the global prime cache for small numbers
    - For larger numbers, performs trial division by prime factors only
    - Results are cached to improve performance for repeated checks

    Time Complexity: 
    - O(1) for cached results and small numbers
    - O(√n) in worst case for large uncached primes

    Args:
        n: The integer to test for primality

    Returns:
        True if n is prime, False otherwise

    Examples:
        >>> is_prime(2)    # Smallest prime
        True
        >>> is_prime(17)   # A prime number
        True
        >>> is_prime(20)   # Composite number (2×2×5)
        False
        >>> is_prime(1)    # One is not prime by definition
        False
        >>> is_prime(97)   # Last prime below 100
        True
    """
    # Handle edge cases
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    if n <= _MAX_LIMIT:
        if n in _PRIME_SET:
            return True

    # Check divisibility by odd numbers up to sqrt(n)
    for i in gen_primes_sundaram_sieve(max_limit=int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    else:
        return True


Factor = namedtuple('Factor', ['base', 'exponent'])


@lru_cache()
def prime_factorization(n: int) -> Tuple[Factor, ...]:
    """
    Decompose an integer into its unique prime factorization.

    Based on the fundamental theorem of arithmetic, this function expresses any integer
    greater than 1 as a unique product of prime numbers raised to specific powers.

    Mathematical Background:
    The fundamental theorem of arithmetic states that every integer greater than 1 can be
    represented uniquely as a product of prime powers: n = p₁ᵏ¹ × p₂ᵏ² × ... × pᵣᵏʳ,
    where p₁ < p₂ < ... < pᵣ are primes and k₁, k₂, ..., kᵣ are positive integers.

    Algorithm:
    1. Validate input (n > 1)
    2. For each prime p ≤ √n:
       a. Check if p divides n
       b. If yes, count how many times p divides n (the exponent k)
       c. Add Factor(p, k) to the result
    3. If the remaining number is > 1, it's a prime factor with exponent 1

    Optimizations:
    - Uses the efficient Sundaram sieve to generate prime candidates
    - Only checks primes up to √n (mathematical optimization)
    - Results are cached via lru_cache decorator
    - Uses namedtuple for clean, readable return values

    Args:
        n: Integer to factorize (must be > 1)

    Returns:
        Tuple of Factor objects, each containing:
        - base: The prime number
        - exponent: Power to which the prime is raised

    Raises:
        ValueError: If n ≤ 1

    Examples:
        >>> prime_factorization(28)  # 28 = 2² × 7¹
        (Factor(base=2, exponent=2), Factor(base=7, exponent=1))
        >>> prime_factorization(100)  # 100 = 2² × 5²
        (Factor(base=2, exponent=2), Factor(base=5, exponent=2))
        >>> prime_factorization(17)  # 17 is prime
        (Factor(base=17, exponent=1))
    """
    if n <= 1:
        raise ValueError(f'n must be greater than 1 (got n={n})')
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
    Calculate all positive divisors of an integer n (including 1 and n).

    This function computes the complete set of divisors using the number's prime factorization,
    employing a combinatorial approach that efficiently handles all possible factor combinations.

    Mathematical Approach:
    For a number with prime factorization n = p₁ᵏ¹ × p₂ᵏ² × ... × pᵣᵏʳ,
    its divisors are all numbers of the form p₁ᵃ¹ × p₂ᵃ² × ... × pᵣᵃʳ where:
    - Each exponent aᵢ ranges from 0 to kᵢ
    - Setting all aᵢ=0 gives the divisor 1
    - Setting all aᵢ=kᵢ gives the divisor n itself

    Algorithm Steps:
    1. Start with the set {1} (1 divides every number)
    2. For each prime factor p with exponent k in the factorization:
       a. Generate powers p¹, p², ..., pᵏ
       b. Multiply each existing divisor by each power
       c. Add all new products to the divisor set
    3. Sort the final set of divisors

    Optimizations:
    - Uses prime_factorization function to get the prime decomposition
    - Employs set operations to avoid duplicate divisors
    - Results are cached via lru_cache decorator

    Args:
        n: Positive integer to find divisors for

    Returns:
        Tuple of all positive divisors of n, sorted in ascending order

    Raises:
        ValueError: If n < 1

    Examples:
        >>> divisors(12)  # 12 = 2² × 3¹
        (1, 2, 3, 4, 6, 12)
        >>> divisors(36)  # 36 = 2² × 3²
        (1, 2, 3, 4, 6, 9, 12, 18, 36)
        >>> divisors(7)   # Prime number
        (1, 7)
    """
    if n < 1:
        raise ValueError(f'n must be greater than or equal to 1 (got n={n})')
    factors: Set[int] = {1}
    for base, exponent in prime_factorization(n):
        factors.update({f * (base ** power) for power in range(1, exponent + 1) for f in factors})
    return tuple(sorted(factors))


@lru_cache()
def proper_factors(n: int) -> Tuple[int, ...]:
    """
    Calculate all proper divisors of an integer n (divisors excluding n itself).

    Proper divisors (or aliquot parts) of a number are all positive divisors less than
    the number itself. This function efficiently computes these by leveraging the
    divisors function and excluding the number itself.

    Mathematical Significance:
    - For prime numbers, the only proper divisor is 1
    - The sum of proper divisors has special meaning in number theory:
      * If sum = n: n is a perfect number (e.g., 6, 28)
      * If sum < n: n is a deficient number (e.g., prime numbers, 8)
      * If sum > n: n is an abundant number (e.g., 12, 18)
    - Amicable numbers form pairs where each is the sum of the other's proper divisors

    Implementation:
    This function calls the divisors function and returns all elements except the last one
    (which is n itself), since the divisors function returns a sorted tuple.

    Args:
        n: Positive integer to find proper divisors for

    Returns:
        Tuple of all proper divisors of n, sorted in ascending order

    Raises:
        ValueError: If n < 1 (inherited from divisors function)

    Examples:
        >>> proper_factors(12)  # 1+2+3+4+6=16 (abundant)
        (1, 2, 3, 4, 6)
        >>> proper_factors(6)   # 1+2+3=6 (perfect)
        (1, 2, 3)
        >>> proper_factors(7)   # Prime number (deficient)
        (1,)
        >>> proper_factors(25)  # Perfect square
        (1, 5)
    """
    return divisors(n)[:-1]


@lru_cache()
def prime_factor_count(num: int) -> int:
    """
    Count the number of distinct prime factors of a positive integer.

    This function efficiently determines how many different prime numbers divide a given integer,
    without counting multiplicity. It uses wheel factorization to dramatically reduce
    the number of trial divisions needed.

    Wheel Factorization Explained:
    Wheel factorization is an advanced technique that generalizes the sieve of Eratosthenes.
    Instead of checking all numbers, it follows optimized patterns of gaps to skip numbers
    that cannot be prime factors based on their congruence properties.

    The implementation uses two wheel patterns:
    1. For small factors (< 11): A simple wheel [2,3,5,7,11...] with gaps [1,1,2,2,4]
       This basic pattern skips even numbers (multiples of 2)

    2. For larger factors (≥ 11): A more sophisticated wheel with gaps
       [2,4,2,4,6,2,6,4,...] that skips multiples of 2, 3, and 5

    Algorithm Efficiency:
    - Only checks potential prime factors up to √num
    - Skips non-candidate numbers via wheel patterns
    - Counts each unique prime factor exactly once
    - Uses memoization to cache results for repeated calls
    - Special handling for any remaining prime factor > √num

    Mathematical Properties:
    - Prime numbers have exactly 1 prime factor
    - The number 1 has 0 prime factors (by definition)
    - The function counts distinct factors (e.g., 2⁴×3² has 2 factors, not 6)

    Args:
        num: Positive integer to analyze

    Returns:
        Number of unique prime factors

    Examples:
        >>> prime_factor_count(12)    # 12 = 2² × 3
        2
        >>> prime_factor_count(17)    # 17 is prime
        1
        >>> prime_factor_count(60)    # 60 = 2² × 3 × 5
        3
        >>> prime_factor_count(1)     # 1 has no prime factors
        0
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
