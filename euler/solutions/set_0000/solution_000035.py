#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 35: circular_primes

Problem Statement:
  The number, 197, is called a circular prime because all rotations of the digits:
  197, 971, and 719, are themselves prime. There are thirteen such primes below
  100: 2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, and 97. How many circular
  primes are there below one million?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=35
Answer: None
"""
from __future__ import annotations

from typing import Set

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sundaram_sieve
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=4,
        is_main_case=False,
        kwargs={'max_limit': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=13,
        is_main_case=False,
        kwargs={'max_limit': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=25,
        is_main_case=False,
        kwargs={'max_limit': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=55,
        is_main_case=False,
        kwargs={'max_limit': 1000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=55,
        is_main_case=False,
        kwargs={'max_limit': 10000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #35
@register_solution(problem_number=35, test_cases=test_cases)
def circular_primes(*, max_limit: int) -> int:
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
        >>> circular_primes(max_limit=10)
        4
        >>> circular_primes(max_limit=100)
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


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(35))
