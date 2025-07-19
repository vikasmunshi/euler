#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 35: Circular primes

Problem Statement:
The number, 197, is called a circular prime because all rotations of the digits: 197, 971, and 719, are themselves
prime. There are thirteen such primes below 100: 2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, and 97.
How many circular primes are there below one million?

Solution Approach:
This implementation efficiently finds circular primes by:
1. Generating all primes below the given limit using the Sundaram sieve algorithm
2. Applying an optimization to exclude numbers with even digits or 5 (except single-digit primes)
3. For each remaining prime, checking if all its digit rotations are also prime

A circular prime is a number where all rotations of its digits are also prime numbers.
For example, 197 is circular because 197, 971, and 719 are all prime.

Test Cases:
- For max_limit=10, the answer is 4 (2, 3, 5, 7)
- For max_limit=100, the answer is 13
- For max_limit=1000, the answer is 25
- For max_limit=1000000, the answer is 55

URL: https://projecteuler.net/problem=35
Answer: 55
"""
from typing import Set

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import gen_primes_sundaram_sieve

# The problem number from Project Euler (https://projecteuler.net/problem=35)
problem_number: int = 35

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_limit': 10},  # There are 4 circular primes below 10: 2, 3, 5, 7
        answer=4,
    ),
    ProblemArgs(
        kwargs={'max_limit': 100},  # 13 circular primes below 100, as listed in the problem description
        answer=13,
    ),
    ProblemArgs(
        kwargs={'max_limit': 1000},  # 25 circular primes below 1000
        answer=25,
    ),
    ProblemArgs(
        kwargs={'max_limit': 10 ** 6},  # The main problem: 55 circular primes below one million
        answer=55,
    ),
    ProblemArgs(
        kwargs={'max_limit': 10 ** 7},  # Note: No new circular primes found between 10^6 and 10^7
        answer=55,
    ),
]


def get_rotated_numbers(*, num: int) -> Set[int]:
    """Generate all possible rotations of the digits of a number.

    This function takes an integer and returns all possible rotations of its digits
    as a set for efficient lookups. A rotation is created by moving digits from the
    beginning to the end of the number.

    For example, for the number 197, it returns the set {197, 971, 719}.
    For single-digit numbers, it returns a set containing only the number itself.

    Args:
        num: The input integer to generate rotations for

    Returns:
        Set of all possible digit rotations of the input number
    """
    str_num: str = str(num)
    # For single-digit numbers, return the set with only the number itself, else return the set of all rotations
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_circular_primes(*, max_limit: int) -> int:
    """
    Count the number of circular primes below the given limit.

    This solution generates all primes below the limit, then filters for circular primes.
    A prime is circular if all its digit rotations are also prime. The implementation uses
    an optimization where numbers containing even digits or 5 (except single-digit primes)
    are immediately excluded, as one of their rotations would be divisible by 2 or 5.

    Args:
        max_limit: An integer representing the upper bound (exclusive)

    Returns:
        The count of circular primes below max_limit

    Example:
        >>> count_circular_primes(max_limit=10)
        4
        >>> count_circular_primes(max_limit=100)
        13
    """
    primes = set(gen_primes_sundaram_sieve(max_limit=max_limit))
    circular_primes = [
        prime for prime in primes
        if prime < 10 or (
                not any(d in str(prime) for d in '024568')
                and not any(rotated_number not in primes for rotated_number in get_rotated_numbers(num=prime))
        )
    ]
    return len(circular_primes)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
