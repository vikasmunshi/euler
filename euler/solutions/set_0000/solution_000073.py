#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 73: counting_fractions_in_a_range

Problem Statement:
  Consider the fraction, \dfrac n d, where n and d are positive integers. If n \lt
  d and \operatorname{HCF}(n, d)=1, it is called a reduced proper fraction. If we
  list the set of reduced proper fractions for d \le 8 in ascending order of size,
  we get: \frac 1 8, \frac 1 7, \frac 1 6, \frac 1 5, \frac 1 4, \frac 2 7, \frac
  1 3, \mathbf{\frac 3 8, \frac 2 5, \frac 3 7}, \frac 1 2, \frac 4 7, \frac 3 5,
  \frac 5 8, \frac 2 3, \frac 5 7, \frac 3 4, \frac 4 5, \frac 5 6, \frac 6 7,
  \frac 7 8 It can be seen that there are 3 fractions between \dfrac 1 3 and
  \dfrac 1 2. How many fractions lie between \dfrac 1 3 and \dfrac 1 2 in the
  sorted set of reduced proper fractions for d \le 12\,000?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=73
Answer: 7295372
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase
from euler.sys_utils import set_resource_limits

test_cases: list[TestCase] = [
    TestCase(
        answer=3,
        is_main_case=False,
        kwargs={'max_d': 8},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=50695,
        is_main_case=False,
        kwargs={'max_d': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=7295372,
        is_main_case=True,
        kwargs={'max_d': 12000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=506608484,
        is_main_case=False,
        kwargs={'max_d': 100000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #73
@register_solution(problem_number=73, test_cases=test_cases[:-1])
def sol_1_counting_fractions_in_a_range(*, max_d: int) -> int:
    """Count fractions between 1/3 and 1/2 using iterative approach.

    Args:
        max_d: Maximum denominator value to consider.

    Returns:
        Number of reduced proper fractions between 1/3 and 1/2.
    """
    lower_denominator: int = 3
    upper_denominator: int = 2
    # initial mediant closest to lower_denominator
    d = upper_denominator + lower_denominator * ((max_d - upper_denominator) // lower_denominator)
    # If `prev_d` and `d` are denominators of adjacent fractions
    # prev_n/prev_d and n/d, then the next denominator is:
    # max_d - (max_d + prev_d) % d
    prev_d = lower_denominator
    count = 0
    # Until we reach the final denominator
    while d != upper_denominator:
        count += 1
        # Shift: the current becomes the previous
        prev_d, d = d, max_d - (max_d + prev_d) % d
    return count


# Register this function as a solution for problem #73
@register_solution(problem_number=73, test_cases=test_cases)
def sol_2_counting_fractions_in_a_range(*, max_d: int) -> int:
    """Count fractions between 1/3 and 1/2 using a rank-based arithmetic approach.

    Args:
        max_d: Maximum denominator value to consider.

    Returns:
        Number of reduced proper fractions between 1/3 and 1/2.
    """

    def rank(n: int, d: int) -> int:
        len_data: int = max_d + 1
        # Initialize the data array
        data: List[int] = [i * n // d for i in range(len_data)]
        # Remove all multiples (similar to sieve of Eratosthenes)
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        # Return the sum of all elements in the data array
        return sum(data)

    return rank(n=1, d=2) - rank(n=1, d=3) - 1


# Register this function as a solution for problem #73
@register_solution(problem_number=73, test_cases=test_cases[:-2])
@set_resource_limits(recursion_var='max_d', multiplier=1, set_int_max_str=False, when='always')
def sol_3_counting_fractions_in_a_range(*, max_d: int) -> int:
    """Count fractions between 1/3 and 1/2 using recursive Farey sequence.

    Args:
        max_d: Maximum denominator value to consider.

    Returns:
        Number of reduced proper fractions between 1/3 and 1/2.
    """

    def recursion(lower_denominator: int, upper_denominator: int) -> int:
        # Check if the denominator exceeds the maximum allowed
        if (mediant := lower_denominator + upper_denominator) > max_d:
            return 0
        # Recursively count mediants
        return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)

    return recursion(lower_denominator=3, upper_denominator=2)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(73))
