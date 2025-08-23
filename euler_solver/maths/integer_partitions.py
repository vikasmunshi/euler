#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integer partition utilities

Helpers for counting and generating integer partitions used in Project Euler
problems. Supports unconstrained partitions, partitions with a maximum part
value, and prime-only partitions. Generation helpers include a safety limit to
avoid excessive memory use, and most functions are memoized for speed.

Public API
- num_partitions(number): total number of partitions p(n) via the pentagonal
  number theorem.
- num_integer_partitions(number, slots): count of partitions with each part
  ≤ slots.
- num_prime_integer_partitions(number, slots): count of partitions using only
  prime parts.
- get_partitions(number, slots, safe_limit=50): generate all partitions with
  each part ≤ slots.
- get_prime_partitions(number, slots, safe_limit=50): generate prime-only
  partitions.

Examples
>>> num_partitions(5)
7
>>> num_integer_partitions(number=5, slots=5)
7
>>> get_partitions(number=4, slots=4)
[[1, 1, 1, 1], [2, 1, 1], [2, 2], [3, 1], [4]]
>>> get_prime_partitions(number=10, slots=10)
[[2, 2, 2, 2, 2], [3, 3, 2, 2], [5, 3, 2], [5, 5], [7, 3]]

Notes
- Memoization: All top-level functions use @lru_cache to speed up recursive
  computation.
- Safety: get_partitions and get_prime_partitions enforce a safe_limit to
  prevent excessive memory usage.
"""
from functools import lru_cache
from typing import Callable, List

from euler_solver.c_libs.gen_primes_sieve_eratosthenes import gen_primes_sieve_eratosthenes
from euler_solver.c_libs.is_prime import is_prime
from euler_solver.c_libs.num_partitions import num_partitions
from euler_solver.logger import logger

num_partitions: Callable[[int], int] = num_partitions


class IntegerPartitionError(ValueError):
    """
    Error raised for invalid arguments to integer partition helpers.

    This exception indicates domain errors such as negative inputs or invalid
    relationships between parameters (e.g., number < slots where slots is the
    maximum allowed part value).
    """
    pass


@lru_cache(maxsize=None)
def num_integer_partitions(*, number: int, slots: int) -> int:
    """
    Count partitions of a number with a maximum part value.

    Computes the number of ways to write number as a sum of positive integers
    where each part is ≤ slots. Uses recursion with memoization.

    Args:
        number (int): The integer to partition.
        slots (int): Maximum allowed part value in the partition.

    Returns:
        int: Count of valid partitions under the constraint.

    Raises:
        IntegerPartitionError: If number or slots is negative, or if number < slots.

    Examples:
        >>> num_integer_partitions(number=5, slots=5)
        7
        >>> num_integer_partitions(number=5, slots=3)
        5  # Allowed: [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]
    """
    if number < 0 or slots < 0:
        raise IntegerPartitionError('number and slots must be non-negative')
    if number < slots:
        raise IntegerPartitionError('number must be greater than or equal to slots')
    if number <= 1:
        return number
    return sum(num_integer_partitions(number=number - n, slots=min(number - n, n))
               for n in range(1, slots + 1)) + (1 if number <= slots else 0)


@lru_cache(maxsize=None)
def num_prime_integer_partitions(*, number: int, slots: int) -> int:
    """
    Count partitions of a number using only prime parts.

    Computes the number of ways to write number as a sum of primes where each
    prime is ≤ slots. Uses recursion with memoization.

    Args:
        number (int): The integer to partition.
        slots (int): Maximum allowed prime value in the partition.

    Returns:
        int: Count of valid prime-only partitions under the constraint.

    Raises:
        IntegerPartitionError: If number or slots is negative.

    Examples:
        >>> num_prime_integer_partitions(number=10, slots=10)
        5
        >>> num_prime_integer_partitions(number=10, slots=5)
        4
    """
    if number < 0 or slots < 0:
        raise IntegerPartitionError('number and slots must be non-negative')
    if number == 0:
        return 1
    if slots < 2:  # 2 is the smallest prime
        return 0
    result = 0
    max_num = min(number, slots)
    for n in gen_primes_sieve_eratosthenes():
        if n > max_num:
            break
        result += num_prime_integer_partitions(number=number - n, slots=n)
    return result


@lru_cache(maxsize=None)
def get_partitions(*, number: int, slots: int, safe_limit: int = 50) -> List[List[int]]:
    """
    Generate all partitions of a number with a maximum part value.

    Returns all ways to write number as a sum of positive integers where each
    part is ≤ slots. A safety limit prevents blowing up memory for large inputs.

    Args:
        number (int): The integer to partition.
        slots (int): Maximum allowed part value in the partition.
        safe_limit (int): Safety threshold to prevent memory issues for large inputs.

    Returns:
        List[List[int]]: All valid partitions as non-increasing lists of integers.

    Raises:
        OverflowError: If number exceeds the safe_limit.
        IntegerPartitionError: If number or slots is negative, or if number < slots.

    Examples:
        >>> get_partitions(number=4, slots=4)
        [[1, 1, 1, 1], [2, 1, 1], [2, 2], [3, 1], [4]]
        >>> get_partitions(number=4, slots=2)
        [[1, 1, 1, 1], [2, 1, 1], [2, 2]]
    """
    if number > safe_limit:
        raise OverflowError(f'number must be less than {safe_limit=}')
    if number < 0 or slots < 0:
        raise IntegerPartitionError('number and slots must be non-negative')
    if number < slots:
        raise IntegerPartitionError('number must be greater than or equal to slots')
    if number <= 1:
        return [] if number == 0 else [[1]]
    partitions: List[List[int]] = []
    for n in range(1, slots + 1):
        if n == number:
            partitions.append([n])
        else:
            for partition in get_partitions(number=number - n, slots=min(number - n, n), safe_limit=safe_limit):
                partitions.append([n] + partition)
    for partition in partitions:
        assert sum(partition) == number, f'{partition=} {sum(partition)=} {number=}'
    return partitions


@lru_cache(maxsize=None)
def get_prime_partitions(*, number: int, slots: int, safe_limit: int = 50) -> List[List[int]]:
    """
    Generate all prime-only partitions of a number under a maximum prime value.

    Returns all ways to write number as a sum of primes where each prime is ≤
    slots. A safety limit prevents excessive memory use on large inputs.

    Args:
        number (int): The integer to partition.
        slots (int): Maximum allowed prime value in the partition.
        safe_limit (int): Safety threshold to prevent memory issues for large inputs.

    Returns:
        List[List[int]]: All valid prime partitions as non-increasing lists of primes.

    Raises:
        OverflowError: If number exceeds the safe_limit.
        IntegerPartitionError: If number or slots is negative.

    Examples:
        >>> get_prime_partitions(number=10, slots=10)
        [[2, 2, 2, 2, 2], [3, 3, 2, 2], [5, 3, 2], [5, 5], [7, 3]]
        >>> get_prime_partitions(number=10, slots=5)
        [[2, 2, 2, 2, 2], [3, 3, 2, 2], [5, 3, 2], [5, 5]]
    """
    if number > safe_limit:
        raise OverflowError(f'number must be less than {safe_limit=}')
    if number < 0 or slots < 0:
        raise IntegerPartitionError('number and slots must be non-negative')
    if number < 2 or slots < 2:  # 2 is the smallest prime
        return []
    prime_partitions: List[List[int]] = []
    max_num = min(number, slots)
    for n in gen_primes_sieve_eratosthenes():
        if n > max_num:
            break
        if n == number:
            prime_partitions.append([n])
        else:
            for partition in get_prime_partitions(number=number - n, slots=min(number - n, n), safe_limit=safe_limit):
                prime_partitions.append([n] + partition)
    for partition in prime_partitions:
        assert sum(partition) == number, f'{partition=} {sum(partition)=} {number=}'
    return prime_partitions


def main() -> int:
    """
    Run internal consistency checks for partition helpers.

    Verifies small known partitions (1–10), cross-checks counts against
    generated lists (including prime-only cases), and spot-checks larger
    values to ensure consistency among implementations.

    Returns:
        int: 0 on successful completion.
    """
    known_partitions = {
        1: [[1]],
        2: [[1, 1], [2]],
        3: [[1, 1, 1], [2, 1], [3]],
        4: [[1, 1, 1, 1], [2, 1, 1], [2, 2], [3, 1], [4]],
        5: [[1, 1, 1, 1, 1], [2, 1, 1, 1], [2, 2, 1], [3, 1, 1], [3, 2], [4, 1], [5]],
        6: [[1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1], [2, 2, 1, 1], [2, 2, 2], [3, 1, 1, 1], [3, 2, 1], [3, 3], [4, 1, 1],
            [4, 2], [5, 1], [6]],
        7: [[1, 1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1], [2, 2, 1, 1, 1], [2, 2, 2, 1], [3, 1, 1, 1, 1], [3, 2, 1, 1],
            [3, 2, 2], [3, 3, 1], [4, 1, 1, 1], [4, 2, 1], [4, 3], [5, 1, 1], [5, 2], [6, 1], [7]],
        8: [[1, 1, 1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1, 1], [2, 2, 1, 1, 1, 1], [2, 2, 2, 1, 1], [2, 2, 2, 2],
            [3, 1, 1, 1, 1, 1], [3, 2, 1, 1, 1], [3, 2, 2, 1], [3, 3, 1, 1], [3, 3, 2], [4, 1, 1, 1, 1], [4, 2, 1, 1],
            [4, 2, 2], [4, 3, 1], [4, 4], [5, 1, 1, 1], [5, 2, 1], [5, 3], [6, 1, 1], [6, 2], [7, 1], [8]],
        9: [[1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1, 1, 1], [2, 2, 1, 1, 1, 1, 1], [2, 2, 2, 1, 1, 1],
            [2, 2, 2, 2, 1], [3, 1, 1, 1, 1, 1, 1], [3, 2, 1, 1, 1, 1], [3, 2, 2, 1, 1], [3, 2, 2, 2], [3, 3, 1, 1, 1],
            [3, 3, 2, 1], [3, 3, 3], [4, 1, 1, 1, 1, 1], [4, 2, 1, 1, 1], [4, 2, 2, 1], [4, 3, 1, 1], [4, 3, 2],
            [4, 4, 1], [5, 1, 1, 1, 1], [5, 2, 1, 1], [5, 2, 2], [5, 3, 1], [5, 4], [6, 1, 1, 1], [6, 2, 1], [6, 3],
            [7, 1, 1], [7, 2], [8, 1], [9]],
        10: [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 1, 1, 1, 1, 1, 1],
             [2, 2, 2, 1, 1, 1, 1], [2, 2, 2, 2, 1, 1], [2, 2, 2, 2, 2], [3, 1, 1, 1, 1, 1, 1, 1],
             [3, 2, 1, 1, 1, 1, 1], [3, 2, 2, 1, 1, 1], [3, 2, 2, 2, 1], [3, 3, 1, 1, 1, 1], [3, 3, 2, 1, 1],
             [3, 3, 2, 2], [3, 3, 3, 1], [4, 1, 1, 1, 1, 1, 1], [4, 2, 1, 1, 1, 1], [4, 2, 2, 1, 1], [4, 2, 2, 2],
             [4, 3, 1, 1, 1], [4, 3, 2, 1], [4, 3, 3], [4, 4, 1, 1], [4, 4, 2], [5, 1, 1, 1, 1, 1], [5, 2, 1, 1, 1],
             [5, 2, 2, 1], [5, 3, 1, 1], [5, 3, 2], [5, 4, 1], [5, 5], [6, 1, 1, 1, 1], [6, 2, 1, 1], [6, 2, 2],
             [6, 3, 1], [6, 4], [7, 1, 1, 1], [7, 2, 1], [7, 3], [8, 1, 1], [8, 2], [9, 1], [10]],
    }
    logger.setLevel('ERROR')
    for number, partitions in known_partitions.items():
        len_partitions = len(partitions)
        prime_partitions = [list_primes for list_primes in partitions if all(is_prime(n) for n in list_primes)]
        len_prime_partitions = len(prime_partitions)
        num_partitions_ = num_partitions(number=number)
        num_integer_partitions_ = num_integer_partitions(number=number, slots=number)
        num_prime_integer_partitions_ = num_prime_integer_partitions(number=number, slots=number)
        partitions_ = get_partitions(number=number, slots=number)
        prime_partitions_ = get_prime_partitions(number=number, slots=number)
        assert partitions_ == partitions, f'{partitions_=} != {partitions=}'
        assert num_partitions_ == len_partitions, f'{num_partitions_=} != {len_partitions=}'
        assert num_integer_partitions_ == len_partitions, f'{num_integer_partitions_=} != {len_partitions=}'
        assert prime_partitions_ == prime_partitions, f'{prime_partitions_=} != {prime_partitions=}'
        assert num_prime_integer_partitions_ == len_prime_partitions, (f'{num_prime_integer_partitions_=} '
                                                                       f'!= {len_prime_partitions=}')

        logger.info(f'partitions for {number=} are correct')
    for number in range(10, 51, 10):
        partitions = get_partitions(number=number, slots=number)
        len_partitions = len(partitions)
        prime_partitions = get_prime_partitions(number=number, slots=number)
        len_prime_partitions = len(prime_partitions)
        num_partitions_ = num_partitions(number=number)
        num_integer_partitions_ = num_integer_partitions(number=number, slots=number)
        num_prime_integer_partitions_ = num_prime_integer_partitions(number=number, slots=number)
        assert num_partitions_ == len_partitions, f'{num_partitions_=} != {len_partitions=}'
        assert num_integer_partitions_ == len_partitions, f'{num_integer_partitions_=} != {len_partitions=}'
        assert num_prime_integer_partitions_ == len_prime_partitions, (f'{num_prime_integer_partitions_=} '
                                                                       f'!= {len_prime_partitions=}')
        logger.info(f'partitions for {number=} are correct')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
