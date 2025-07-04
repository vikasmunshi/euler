#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prime number utility module for Project Euler problems.

This module provides functions for working with prime numbers, including:
- Generating prime numbers using the Sieve of Sundaram
- Testing primality of numbers
- Computing prime factorizations
- Finding divisors and proper factors of numbers
- Counting prime factors

The module uses caching strategies to optimize repeated operations:
- Prime numbers are cached in memory and persisted to disk
- Function results are cached using lru_cache decorators
- A shared cache dictionary tracks generated primes for reuse

Example usage:
    >>> from euler.primes import is_prime, prime_factorization, divisors
    >>> is_prime(17)
    True
    >>> prime_factorization(60)
    (Factor(base=2, exponent=2), Factor(base=3, exponent=1), Factor(base=5, exponent=1))
    >>> divisors(28)
    (1, 2, 4, 7, 14, 28)
"""
import pathlib
from collections import namedtuple
from functools import lru_cache
from itertools import takewhile
from typing import Tuple, Set

from euler.logger import logger

_CACHE = {
    'primes': tuple(),  # Tuple of prime numbers up to max_limit
    'primes_set': set(),  # Set of prime numbers for O(1) lookups
    'max_limit': 0,  # Maximum value for which primes have been generated
}

__MAX_LIMIT: int = int(1.0e8)  # Default maximum limit for prime generation (100 million)


def seed_cache(max_limit: int = __MAX_LIMIT, regenerate: bool = False) -> None:
    """Initialize or reload the prime number cache.

    This function either loads prime numbers from the primes.txt file or
    generates them using the Sundaram sieve algorithm. The generated primes
    are stored both in memory (in the _CACHE dictionary) and on disk for future use.

    Args:
        max_limit: The maximum number up to which to generate primes.
            Defaults to __MAX_LIMIT (100 million).
        regenerate: If True, forces regeneration of primes even if the cache file exists.
            Defaults to False.

    Side effects:
        - Updates the global _CACHE dictionary with prime numbers
        - May create or update the primes.txt file
        - Logs information about the operation
    """
    primes_file: pathlib.Path = pathlib.Path(__file__).parent / 'primes.txt'
    if regenerate or not primes_file.exists():
        with open(primes_file, 'w') as out_file:
            out_file.write(f'{max_limit=}\n')
            primes = gen_primes_sundaram_sieve(max_limit=max_limit)
            out_file.write('\n'.join(f'{prime}' for prime in primes))
        logger.info(f'wrote primes up to {max_limit:,} to {primes_file}')
    with open(primes_file, 'r') as in_file:
        _CACHE['max_limit'] = int(in_file.readline().split('=')[-1])
        _CACHE['primes'] = primes = tuple(int(p) for p in in_file.read().splitlines(keepends=False))
        _CACHE['primes_set'] = set(primes)
        logger.info(f'loaded primes up to {max_limit:,} from {primes_file}, {primes[0]=:,} {primes[-1]=:,}')


def gen_primes_sundaram_sieve(*, max_limit: int) -> Tuple[int, ...]:
    """Generate prime numbers up to max_limit using the Sieve of Sundaram.

    The Sieve of Sundaram is an algorithm for finding all prime numbers up to a
    specified integer. It operates by marking numbers of the form i+j+2ij as composite
    and then deriving primes from the unmarked numbers.

    Args:
        max_limit: The maximum value up to which to generate prime numbers.

    Returns:
        A tuple of prime numbers up to max_limit.

    Notes:
        - If max_limit is less than or equal to the current _CACHE['max_limit'],
          returns primes from the cache instead of regenerating them.
        - Updates the global _CACHE with newly generated primes if max_limit is greater
          than the current cache limit.
        - Time complexity: O(n log log n) where n is max_limit.
    """
    if max_limit > _CACHE['max_limit']:
        max_number = (max_limit - 1) // 2 + 1
        numbers = list(range(0, max_number))
        for i in range(1, max_number):
            for j in range(i, max_number):
                index = i + j + (2 * i * j)
                if index < max_number:
                    numbers[index] = 0
                else:
                    break
        primes = (2,) + tuple(2 * n + 1 for n in numbers[1:] if n != 0)
        _CACHE['max_limit'] = max_limit
        _CACHE['primes'] = primes
        _CACHE['primes_set'] = set(primes)
        logger.info(f'generated primes {max_limit=:,} using sundaram sieve: {len(primes)=:,} {primes[-1]=:,}')
    return tuple(takewhile(lambda p: p <= max_limit, _CACHE['primes']))


@lru_cache()
def is_prime(n: int) -> bool:
    """Determine whether a number is prime.

    A prime number is a natural number greater than 1 that is not divisible
    by any positive integers other than 1 and itself.

    This function first checks if the number is in the cached set of primes.
    If not, it tests divisibility by all primes up to the square root of n.

    Args:
        n: The number to test for primality.

    Returns:
        True if n is prime, False otherwise.

    Examples:
        >>> is_prime(2)
        True
        >>> is_prime(4)
        False
        >>> is_prime(17)
        True

    Notes:
        - Results are cached for efficiency in repeated calls.
        - For large numbers not in the cache, this regenerates primes up to sqrt(n).
    """
    if n <= _CACHE['max_limit']:
        return n in _CACHE['primes_set']
    else:
        max_divisor = int(n ** 0.5) + 1
        if max_divisor > _CACHE['max_limit']:
            logger.info(f'got a number {n=:,} that is too large for the cache, regenerating primes')
        for p in gen_primes_sundaram_sieve(max_limit=int(n ** 0.5) + 1):
            if n % p == 0:
                return False
        else:
            return True


# A namedtuple representing a prime factor with its base and exponent
# For example, Factor(base=2, exponent=3) represents 2³ = 8
Factor = namedtuple('Factor', ['base', 'exponent'])


@lru_cache()
def prime_factorization(n: int) -> Tuple[Factor, ...]:
    """Compute the prime factorization of a number.

    This function decomposes a number into its prime factors, expressing each factor
    as a base-exponent pair. The factorization is returned as a tuple of Factor objects.

    Args:
        n: The number to factorize. Must be greater than 1.

    Returns:
        A tuple of Factor objects representing the prime factorization.
        Each Factor contains a prime base and its corresponding exponent.

    Raises:
        ValueError: If n is less than or equal to 1.

    Examples:
        >>> prime_factorization(60)
        (Factor(base=2, exponent=2), Factor(base=3, exponent=1), Factor(base=5, exponent=1))
        # 60 = 2² × 3¹ × 5¹

    Notes:
        - Results are cached for efficiency in repeated calls.
        - Uses gen_primes_sundaram_sieve to generate primes up to sqrt(n).
        - Time complexity: O(sqrt(n)).
    """
    if n <= 1:
        raise ValueError(f'n must be greater than 1 (got n={n})')
    factors = []

    for prime in gen_primes_sundaram_sieve(max_limit=int(n ** 0.5) + 1):  # Iterate over primes up to sqrt(n)
        if prime > n:
            break
        exponent = 0
        while n % prime == 0:
            n //= prime
            exponent += 1
        if exponent > 0:
            factors.append(Factor(base=prime, exponent=exponent))
    if n > 1:
        factors.append(Factor(base=n, exponent=1))

    return tuple(factors)


@lru_cache()
def divisors(n: int) -> Tuple[int, ...]:
    """Calculate all divisors of a number.

    This function computes all positive integers that divide the input number n
    without a remainder, including 1 and n itself.

    Args:
        n: The number to find divisors for. Must be greater than or equal to 1.

    Returns:
        A sorted tuple of all divisors of n.

    Raises:
        ValueError: If n is less than 1.

    Examples:
        >>> divisors(28)
        (1, 2, 4, 7, 14, 28)

    Notes:
        - Results are cached for efficiency in repeated calls.
        - This implementation uses the prime factorization of n to generate all divisors.
        - Time complexity: O(d log d) where d is the number of divisors (for sorting).
    """
    if n < 1:
        raise ValueError(f'n must be greater than or equal to 1 (got n={n})')
    factors: Set[int] = {1}
    for base, exponent in prime_factorization(n):
        factors.update({f * (base ** power) for power in range(1, exponent + 1) for f in factors})
    return tuple(sorted(factors))


@lru_cache()
def proper_factors(n: int) -> Tuple[int, ...]:
    """Calculate all proper divisors of a number.

    Proper divisors are positive integers that divide the input number n
    without a remainder, excluding n itself. For example, the proper divisors
    of 28 are 1, 2, 4, 7, and 14.

    Args:
        n: The number to find proper divisors for. Must be greater than or equal to 1.

    Returns:
        A sorted tuple of all proper divisors of n.

    Examples:
        >>> proper_factors(28)
        (1, 2, 4, 7, 14)

    Notes:
        - Results are cached for efficiency in repeated calls.
        - This function simply calls divisors(n) and excludes the last element (n itself).
    """
    return divisors(n)[:-1]


@lru_cache()
def prime_factor_count(num: int) -> int:
    """Count the number of unique prime factors of a number.

    This function determines how many distinct prime numbers divide the input number.
    For example, 28 = 2² × 7 has two unique prime factors: 2 and 7.

    Args:
        num: The number to count prime factors for.

    Returns:
        The count of unique prime factors.

    Examples:
        >>> prime_factor_count(28)
        2
        >>> prime_factor_count(60)  # 60 = 2² × 3 × 5
        3

    Notes:
        - Results are cached for efficiency in repeated calls.
        - Uses a wheel factorization approach with optimized increments to test factors.
        - Time complexity: O(sqrt(num)).
    """
    factor, num_factors = 1, 0
    while factor <= int(num ** 0.5):
        for gap in ([1, 1, 2, 2, 4] if factor < 11 else [2, 4, 2, 4, 6, 2, 6, 4]):
            factor, is_new_factor = factor + gap, True
            while num % factor == 0:
                num //= factor
                if is_new_factor:
                    num_factors, is_new_factor = num_factors + 1, False
    return num_factors + (0 if num == 1 else 1)


if __name__ == '__main__':
    # When module is run directly, seed the cache with primes up to __MAX_LIMIT
    logger.setLevel('INFO')
    seed_cache(max_limit=__MAX_LIMIT, regenerate=True)
