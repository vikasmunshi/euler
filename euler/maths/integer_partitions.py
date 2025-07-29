#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integer Partitioning Module

This module provides functions for working with integer partitions - ways of writing
an integer as a sum of positive integers. It includes functions for both counting
and generating all possible partitions, with additional support for partitions
consisting only of prime numbers.

Functions:
    num_partitions(number): Calculate the total number of partitions for a given integer
        using the pentagonal number theorem.

    num_integer_partitions(number, slots): Count partitions with constraints on the
        maximum value in the partition (slots).

    num_prime_integer_partitions(number, slots): Count partitions consisting only of
        prime numbers.

    get_partitions(number, slots, safe_limit): Generate all partitions of a number with
        maximum value constraint.

    get_prime_partitions(number, slots, safe_limit): Generate all partitions consisting
        only of prime numbers.

Examples:
    >>> num_partitions(5)
    7
    >>> num_integer_partitions(number=5, slots=5)
    7
    >>> get_partitions(number=4, slots=4)
    [[1, 1, 1, 1], [2, 1, 1], [2, 2], [3, 1], [4]]
    >>> get_prime_partitions(number=10, slots=10)
    [[2, 2, 2, 2, 2], [2, 3, 5], [3, 7], [5, 5]]

Note:
    All functions use memoization (@lru_cache) to improve performance with recursive calls.
    The get_partitions and get_prime_partitions functions include a safety limit to prevent
    memory issues with large numbers.
"""
from functools import lru_cache
from itertools import count
from typing import List

from euler.logger import logger
from euler.maths.primes import gen_primes_sieve, is_prime
from euler.types import EulerError


class IntegerPartitionError(EulerError):
    pass


@lru_cache(maxsize=None)
def num_partitions(number: int) -> int:
    """
    Calculate the total number of integer partitions for a given number.

    This function implements the pentagonal number theorem to efficiently compute
    the number of ways to partition an integer into sums of positive integers.
    Uses a recursive approach with memoization for performance.

    Args:
        number: The integer to partition

    Returns:
        The total number of distinct partitions

    Examples:
        >>> num_partitions(4)
        5  # [4], [3,1], [2,2], [2,1,1], [1,1,1,1]
        >>> num_partitions(5)
        7
    """
    if number <= 0:
        return int(number == 0)
    result = 0
    for n in count(1):
        _n, sign = -n, (-1, +1)[n % 2]
        p_1, p_2 = num_partitions(number - (n * (3 * n - 1) // 2)), num_partitions(number - (_n * (3 * _n - 1) // 2))
        result += sign * (p_1 + p_2)
        if p_1 == 0 and p_2 == 0:
            break
    return result


@lru_cache(maxsize=None)
def num_integer_partitions(*, number: int, slots: int) -> int:
    """
    Count the number of ways to partition an integer with a maximum value constraint.

    This function calculates the number of different ways to write 'number' as a sum of
    positive integers where no integer in the partition exceeds 'slots'.
    Uses dynamic programming with recursion and memoization.

    Args:
        number: The integer to partition
        slots: The maximum value allowed in any partition

    Returns:
        The count of valid partitions

    Raises:
        IntegerPartitionError: If number or slots is negative, or if number < slots

    Examples:
        >>> num_integer_partitions(number=5, slots=5)
        7
        >>> num_integer_partitions(number=5, slots=3)
        5  # Only partitions with values ≤ 3: [3,2], [3,1,1], [2,2,1], [2,1,1,1], [1,1,1,1,1]
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
    Count the number of ways to partition an integer using only prime numbers.

    This function calculates the number of different ways to write 'number' as a sum of
    prime numbers where no prime in the partition exceeds 'slots'.
    Uses dynamic programming with recursion and memoization.

    Args:
        number: The integer to partition
        slots: The maximum prime value allowed in any partition

    Returns:
        The count of valid prime partitions

    Raises:
        IntegerPartitionError: If number or slots is negative

    Examples:
        >>> num_prime_integer_partitions(number=10, slots=10)
        4  # [2,2,2,2,2], [2,3,5], [3,7], [5,5]
        >>> num_prime_integer_partitions(number=10, slots=5)
        2  # [5,5], [2,3,5]
    """
    if number < 0 or slots < 0:
        raise IntegerPartitionError('number and slots must be non-negative')
    if number == 0:
        return 1
    if slots < 2:  # 2 is the smallest prime
        return 0
    result = 0
    max_num = min(number, slots)
    for n in gen_primes_sieve():
        if n > max_num:
            break
        result += num_prime_integer_partitions(number=number - n, slots=n)
    return result


@lru_cache(maxsize=None)
def get_partitions(*, number: int, slots: int, safe_limit: int = 50) -> List[List[int]]:
    """
    Generate all possible partitions of a number with a maximum value constraint.

    This function returns all the different ways to write 'number' as a sum of
    positive integers where no integer in the partition exceeds 'slots'.
    Includes a safety limit to prevent memory issues with large numbers.

    Args:
        number: The integer to partition
        slots: The maximum value allowed in any partition
        safe_limit: Safety threshold to prevent memory issues with large numbers

    Returns:
        A list of all valid partitions, where each partition is a list of integers

    Raises:
        OverflowError: If number exceeds the safe_limit
        IntegerPartitionError: If number or slots is negative, or if number < slots

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
    Generate all possible partitions of a number using only prime numbers.

    This function returns all the different ways to write 'number' as a sum of
    prime numbers where no prime in the partition exceeds 'slots'.
    Includes a safety limit to prevent memory issues with large numbers.

    Args:
        number: The integer to partition
        slots: The maximum prime value allowed in any partition
        safe_limit: Safety threshold to prevent memory issues with large numbers

    Returns:
        A list of all valid prime partitions, where each partition is a list of prime integers

    Raises:
        OverflowError: If number exceeds the safe_limit
        IntegerPartitionError: If number or slots is negative

    Examples:
        >>> get_prime_partitions(number=10, slots=10)
        [[2, 2, 2, 2, 2], [2, 3, 5], [3, 7], [5, 5]]
        >>> get_prime_partitions(number=10, slots=5)
        [[2, 3, 5], [5, 5]]
    """
    if number > safe_limit:
        raise OverflowError(f'number must be less than {safe_limit=}')
    if number < 0 or slots < 0:
        raise IntegerPartitionError('number and slots must be non-negative')
    if number < 2 or slots < 2:  # 2 is the smallest prime
        return []
    prime_partitions: List[List[int]] = []
    max_num = min(number, slots)
    for n in gen_primes_sieve():
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
    Main test function to verify the correctness of partition functions.

    This function tests all the partition functions against known values for small integers,
    and also verifies the consistency between different calculation methods.

    The function performs several types of verification:
    1. Compares generated partitions against pre-defined expected values for numbers 1-10
    2. Verifies that the count functions match the actual number of partitions
    3. Tests prime partitions against filtered partitions containing only prime numbers
    4. Tests larger numbers (10-50) to ensure consistency across different calculation methods

    Returns:
        0 on successful completion
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
