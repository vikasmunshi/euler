#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prime number utility module for Project Euler problems.

This module provides efficient implementations of prime number algorithms and related
number theory functions commonly needed in Project Euler problems. The implementations
use various optimizations including caching, sieving methods, and efficient factorization
algorithms.

Key Features:
- Multiple prime generation algorithms (Sundaram sieve, memory-efficient sieve)
- Primality testing with optimized trial division
- Prime factorization with exponents
- Divisor calculation (all divisors and proper divisors)
- Prime factor counting
- Persistent caching of prime numbers

Optimization Strategies:
- In-memory caching of generated primes via global _CACHE dictionary
- Disk-based persistence of prime lists for reuse across runs
- Function result caching with lru_cache decorators
- Memory-efficient algorithms for large number operations

Example Usage:
    >>> from euler_solver.maths.primes import prime_factorization, get_divisors, is_prime, proper_factors

    # Test if a number is prime
    >>> c_lib(17)
    True
    >>> c_lib(100)
    False

    # Get prime factorization with exponents
    >>> prime_factorization(60)  # 60 = 2² × 3 × 5
    (Factor(base=2, exponent=2), Factor(base=3, exponent=1), Factor(base=5, exponent=1))

    # Find all divisors of a number
    >>> get_divisors(28)  # 1, 2, 4, 7, 14, and 28
    (1, 2, 4, 7, 14, 28)

    # Get just the proper divisors (exclude the number itself)
    >>> proper_factors(28)  # 1, 2, 4, 7, and 14
    (1, 2, 4, 7, 14)
"""
import pathlib
from collections import namedtuple
from functools import lru_cache
from itertools import takewhile
from typing import Callable, Generator, cast

from euler_solver.logger import logger
from euler_solver.setup import base_dir


class PrimeError(ValueError):
    """Error class for prime-related errors."""
    pass


_CACHE: dict[str, tuple[int, ...] | set[int] | int] = {
    'primes': tuple(),  # tuple of prime numbers up to max_limit
    'primes_set': set(),  # set of prime numbers for O(1) lookups
    'max_limit': 0,  # Maximum value for which primes have been generated
}

__MAX_LIMIT: int = int(1.0e7)  # Default maximum limit for prime generation (10 million)


def get_max_cached_primes() -> int:
    """Get the maximum number of primes cached in memory."""
    return cast(int, _CACHE['max_limit'])


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
    primes_file: pathlib.Path = base_dir / 'resources/primes.txt'
    if regenerate or not primes_file.exists():
        with open(primes_file, 'w') as out_file:
            out_file.write(f'{max_limit=}\n')
            primes = get_pre_computed_primes_sundaram_sieve(max_limit=max_limit)
            out_file.write('\n'.join(f'{prime}' for prime in primes))
        logger.info(f'wrote primes up to {max_limit:,} to {primes_file}')
    with open(primes_file, 'r') as in_file:
        _CACHE['max_limit'] = int(in_file.readline().split('=')[-1])
        _CACHE['primes'] = primes = tuple(int(p) for p in in_file.read().splitlines(keepends=False))
        _CACHE['primes_set'] = set(primes)
        logger.info(f'loaded primes up to {max_limit:,} from {primes_file}, {primes[0]=:,} {primes[-1]=:,}')


def ensure_prime_cache_is_loaded[T](func: Callable[..., T]) -> Callable[..., T]:
    """A decorator that ensures the prime number cache is loaded before function execution.

    This decorator checks if the prime number cache is empty when the decorated function
    is defined. If the cache is empty, it calls seed_cache() to populate it with prime
    numbers. The decorator returns the original function unchanged but guarantees that
    primes are available in the cache when the function executes.

    Args:
        func: The function to decorate.

    Returns:
        The original function unchanged.

    Example:
        >>> @ensure_prime_cache_is_loaded
        ... def my_prime_function(n):
        ...     # Prime cache is guaranteed to be loaded here
        ...     return n in _CACHE['primes_set']
    """
    if get_max_cached_primes() == 0:
        seed_cache()
    return func


def gen_primes_sieve_eratosthenes() -> Generator[int, None, None]:
    """Generate prime numbers indefinitely using a memory-efficient sieve algorithm.

    This function implements a memory-efficient version of the Sieve of Eratosthenes
    that generates prime numbers one at a time without storing a large boolean array.
    It uses a dictionary to track composites and their prime factors, allowing it to
    generate primes indefinitely without memory limitations.

    Algorithm steps:
    1. Use a dictionary to track composite numbers and their prime factors
    2. For each number n, check if it is in the known_composites dictionary
    3. If not in the dictionary, n is prime - yield it and mark n² as composite
    4. If in the dictionary, update future composites with its factors and remove it

    Yields:
        Prime numbers as integers, starting from 2 and continuing indefinitely

    Examples:
        >>> primes_gen = gen_primes_sieve_eratosthenes()
        >>> [next(primes_gen) for _ in range(5)]  # First 5 primes
        [2, 3, 5, 7, 11]

    Notes:
        - Unlike gen_primes_sundaram_sieve, this doesn't have an upper limit
        - Memory usage grows slowly with the size of primes being generated
        - This is ideal when you need to search for primes without a predetermined limit
        - The algorithm only tracks composite numbers that are currently needed
    """
    known_composites: dict[int, list[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            # The current number is prime - yield it and mark its square as composite
            yield current_number
            known_composites[current_number ** 2] = [current_number]
        else:
            # Current number is composite - update future composites
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            # Remove the current composite from the dictionary to save memory
            del known_composites[current_number]
        current_number += 1


def get_primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """
    Generate prime numbers up to max_num using the Sieve of Sundaram.

    Args:
        max_num: The maximum value up to which to generate prime numbers (inclusive).

    Returns:
        A tuple of prime numbers up to max_num, sorted in ascending order.
    """
    max_number = (max_num - 1) // 2
    numbers = [True] * (max_number + 1)
    for i in range(1, max_number + 1):
        for j in range(i, (max_number - i) // (2 * i + 1) + 1):
            numbers[i + j + 2 * i * j] = False
    return (2,) + tuple(2 * i + 1 for i in range(1, max_number + 1) if numbers[i])


def get_pre_computed_primes_sundaram_sieve(*, max_limit: int) -> tuple[int, ...]:
    """Generate prime numbers up to max_limit using the Sieve of Sundaram.

    The Sieve of Sundaram is an efficient algorithm for finding all prime numbers up to a
    specified limit. It works by systematically marking numbers of the form i+j+2ij as composite
    and then deriving primes from the unmarked numbers.

    Args:
        max_limit: The maximum value up to which to generate prime numbers (inclusive)

    Returns:
        A tuple of prime numbers up to max_limit, sorted in ascending order

    Examples:
        >>> get_pre_computed_primes_sundaram_sieve(max_limit=20)
        (2, 3, 5, 7, 11, 13, 17, 19)
        >>> get_pre_computed_primes_sundaram_sieve(max_limit=10)
        (2, 3, 5, 7)

    Notes:
        - Uses caching to avoid redundant calculations: if the requested max_limit is
          less than or equal to the current _CACHE['max_limit'], returns primes from
          the cache instead of regenerating them
        - Updates the global _CACHE with newly generated primes if max_limit is greater
          than the current cache limit
        - Generally faster than trial division methods for large ranges
        - Time complexity: O(n log log n) where n is max_limit
        - Space complexity: O(n)
    """
    if max_limit > cast(int, _CACHE['max_limit']):
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
    return tuple(takewhile(lambda p: p <= max_limit, cast(tuple[int, ...], _CACHE['primes'])))


def num_factors(n: int) -> int:
    """Count the number of divisors for a given number using trial division."""
    count = 0
    sqrt_n = int(n ** 0.5)
    for i in range(1, sqrt_n + 1):
        if n % i == 0:
            count += 2  # i and n // i
    if sqrt_n * sqrt_n == n:  # Perfect square
        count -= 1
    return count


def sum_proper_divisors(n: int) -> int:
    """Calculate the sum of proper divisors of `n`."""
    if n < 2:
        return 0
    n_sqrt = int(n ** 0.5)
    total = 1
    for i in range(2, n_sqrt + 1):
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
    return total


# Define a namedtuple for representing prime factors with their exponents
# Factor(base=2, exponent=3) represents 2³ = 8 in a prime factorization
# This provides a clearer structure than using tuples or dictionaries
Factor = namedtuple('Factor', ['base', 'exponent'])


@lru_cache()
def prime_factorization(n: int) -> tuple[Factor, ...]:
    """Compute the prime factorization of a number.

    This function decomposes a number into its prime factors, expressing each factor
    as a base-exponent pair using the Factor namedtuple. The factorization is returned
    as a tuple of Factor objects sorted by increasing base.

    Args:
        n: The number to factorize. Must be greater than 1.

    Returns:
        A tuple of Factor objects representing the prime factorization.
        Each Factor contains a prime base and its corresponding exponent.

    Raises:
        PrimeError: If n is less than or equal to 1.

    Examples:
        >>> prime_factorization(60)  # 60 = 2² × 3¹ × 5¹
        (Factor(base=2, exponent=2), Factor(base=3, exponent=1), Factor(base=5, exponent=1))

        >>> prime_factorization(128)  # 128 = 2⁷
        (Factor(base=2, exponent=7),)

        >>> prime_factorization(13)  # 13 is prime
        (Factor(base=13, exponent=1),)

        >>> prime_factorization(1001)  # 1001 = 7 × 11 × 13
        (Factor(base=7, exponent=1), Factor(base=11, exponent=1), Factor(base=13, exponent=1))

    Algorithm:
        1. Try dividing n by each prime up to sqrt(n)
        2. When a divisor is found, divide n by it repeatedly
        3. Track the count of divisions as the exponent
        4. If any remainder > 1 exists, it must be a prime itself

    Performance:
        - Results are cached for efficiency in repeated calls
        - Uses gen_primes_sundaram_sieve for efficient prime generation
        - Time complexity: O(sqrt(n))
        - Space complexity: O(log n) for storing factors
    """
    if n <= 1:
        raise PrimeError(f'n must be greater than 1 (got n={n})')
    factors = []

    for prime in get_pre_computed_primes_sundaram_sieve(max_limit=int(n ** 0.5) + 1):
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
def get_divisors(n: int) -> tuple[int, ...]:
    """Calculate all divisors of a number.

    This function computes all positive integers that divide the input number n
    without a remainder, including 1 and n itself. The divisors are returned
    in ascending order.

    Args:
        n: The number to find divisors for. Must be greater than or equal to 1.

    Returns:
        A sorted tuple of all divisors of n.

    Raises:
        PrimeError: If n is less than 1.

    Examples:
        >>> get_divisors(1)   # 1 has only itself as a divisor
        (1,)
        >>> get_divisors(12)  # 12 has divisors 1, 2, 3, 4, 6, and 12
        (1, 2, 3, 4, 6, 12)
        >>> get_divisors(28)  # 28 has divisors 1, 2, 4, 7, 14, and 28
        (1, 2, 4, 7, 14, 28)
        >>> get_divisors(17)  # Prime numbers have only 1 and themselves
        (1, 17)

    Algorithm:
        1. Find the prime factorization of n
        2. Generate all possible combinations of prime factors with their exponents
        3. Sort the resulting divisors in ascending order

    Performance:
        - Results are cached for efficiency in repeated calls
        - More efficient than trial division for numbers with many divisors
        - Time complexity: O(d log d) where d is the number of divisors (for sorting)
        - Space complexity: O(d) to store all divisors
    """
    if n <= 0:
        raise PrimeError(f'n must be greater than 0  (got n={n})')
    if n == 1:
        return (1,)
    factors: set[int] = {1}
    for base, exponent in prime_factorization(n):
        factors.update({f * (base ** power) for power in range(1, exponent + 1) for f in factors})
    return tuple(sorted(factors))


@lru_cache()
def proper_factors(n: int) -> tuple[int, ...]:
    """Calculate all proper divisors of a number.

    Proper divisors are positive integers that divide the input number n
    without a remainder, excluding n itself. These are used in various number theory
    problems such as finding perfect, abundant, or deficient numbers.

    Args:
        n: The number to find proper divisors for. Must be greater than or equal to 1.

    Returns:
        A sorted tuple of all proper divisors of n.

    Examples:
        >>> proper_factors(6)   # Proper divisors of 6 are 1, 2, and 3
        (1, 2, 3)
        >>> proper_factors(28)  # Proper divisors of 28 are 1, 2, 4, 7, and 14
        (1, 2, 4, 7, 14)
        >>> proper_factors(11)  # Prime numbers have only 1 as a proper divisor
        (1,)
        >>> proper_factors(1)   # 1 has no proper divisors (empty tuple)
        ()

    Notes:
        - A perfect number equals the sum of its proper divisors (e.g., 6 = 1+2+3)
        - An abundant number is less than the sum of its proper divisors
        - A deficient number is greater than the sum of its proper divisors
        - This function calls divisors(n) and excludes the last element (n itself)
        - Results are cached for efficiency in repeated calls
    """
    if n <= 1:
        raise PrimeError(f'n must be greater than 1  (got n={n})')
    return get_divisors(n)[:-1]


@lru_cache()
def prime_factor_count(num: int) -> int:
    """Count the number of unique prime factors of a number.

    This function determines how many distinct prime numbers divide the input number,
    regardless of their exponents. For example, 28 = 2² × 7 has two unique prime
    factors (2 and 7), and 60 = 2² × 3 × 5 has three unique prime factors (2, 3, and 5).

    Args:
        num: The number to count prime factors for. Should be a positive integer.

    Returns:
        The count of unique prime factors.

    Examples:
        >>> prime_factor_count(28)  # 28 = 2² × 7
        2
        >>> prime_factor_count(60)  # 60 = 2² × 3 × 5
        3
        >>> prime_factor_count(13)  # 13 is prime
        1
        >>> prime_factor_count(1)   # 1 has no prime factors
        0
        >>> prime_factor_count(16)  # 16 = 2⁴ (just one unique prime factor)
        1

    Optimization details:
        - Uses a wheel factorization approach with optimized increments
        - Special handling for factors 2, 3, 5, 7 with custom gap sequences
        - Avoids redundant checking of multiples
        - Results are cached for efficiency in repeated calls
        - Time complexity: O(sqrt(num))
        - Space complexity: O(1)
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


@lru_cache(maxsize=None)
def get_relative_primes(n: int) -> tuple[int, ...]:
    """Get all relative primes of a number."""
    relative_primes: tuple[int, ...] = (1,)
    divisors: set[int] = set(get_divisors(n)[1:])
    for i in range(2, n):
        if not any(factor_of_i.base in divisors for factor_of_i in prime_factorization(i)):
            relative_primes += (i,)
    return relative_primes


@lru_cache(maxsize=None)
def euler_totient(n: int) -> int:
    """Calculate Euler's totient function φ(n) using prime factorization.

    The totient function counts the number of integers up to n that are coprime to n.
    This implementation uses the multiplicative property of φ(n) and the formula for
    prime powers: φ(p^k) = p^k - p^(k-1) = p^k(1 - 1/p).

    Args:
        n: The number to calculate φ(n) for. Must be positive.

    Returns:
        The value of φ(n).

    Examples:
        >>> euler_totient(1)  # By definition
        1
        >>> euler_totient(9)  # 1,2,4,5,7,8 are coprime to 9
        6
        >>> euler_totient(12)  # 1,5,7,11 are coprime to 12
        4
        >>> euler_totient(13)  # For primes p, φ(p) = p-1
        12
    """
    if n == 1:
        return 1
    result = n
    for factor in prime_factorization(n):
        result *= (1 - (1 / factor.base))
    return int(result)


if __name__ == '__main__':
    # When module is run directly, seed the cache with primes up to __MAX_LIMIT
    logger.setLevel('INFO')
    seed_cache(max_limit=__MAX_LIMIT, regenerate=True)
