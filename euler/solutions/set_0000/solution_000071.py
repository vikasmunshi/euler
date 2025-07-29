#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 71: ordered_fractions

Problem Statement:
  Consider the fraction, \dfrac n d, where n and d are positive integers. If n \lt
  d and \operatorname{HCF}(n,d)=1, it is called a reduced proper fraction. If we
  list the set of reduced proper fractions for d \le 8 in ascending order of size,
  we get: \frac 1 8, \frac 1 7, \frac 1 6, \frac 1 5, \frac 1 4, \frac 2 7, \frac
  1 3, \frac 3 8, \mathbf{\frac 2 5}, \frac 3 7, \frac 1 2, \frac 4 7, \frac 3 5,
  \frac 5 8, \frac 2 3, \frac 5 7, \frac 3 4, \frac 4 5, \frac 5 6, \frac 6 7,
  \frac 7 8 It can be seen that \dfrac 2 5 is the fraction immediately to the left
  of \dfrac 3 7. By listing the set of reduced proper fractions for d \le
  1\,000\,000 in ascending order of size, find the numerator of the fraction
  immediately to the left of \dfrac 3 7.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=71
Answer: None
"""
from __future__ import annotations

from fractions import Fraction

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=2,
        is_main_case=False,
        kwargs={'max_d': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=428570,
        is_main_case=False,
        kwargs={'max_d': 1000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=428571425,
        is_main_case=False,
        kwargs={'max_d': 1000000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=428571428570,
        is_main_case=False,
        kwargs={'max_d': 1000000000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #71
@register_solution(problem_number=71, test_cases=test_cases)
def ordered_fractions(*, max_d: int) -> int:
    """Find the numerator of the reduced proper fraction immediately to the left of 3/7.

    The function uses a direct mathematical approach to efficiently find the fraction
    immediately to the left of 3/7 with denominator < max_d.

    Mathematical approach:
    1. We start with our target fraction 3/7
    2. To get as close as possible to 3/7 but still below it, we need the denominator
       to be divisible by 7 (to ensure the result is in lowest form)
    3. We find the largest multiple of 7 that is less than max_d
    4. The fraction (3/7 - 1/largest_multiple_of_7) gives us the closest reduced
       proper fraction to the left of 3/7

    Args:
        max_d: The maximum denominator value to consider

    Returns:
        The numerator of the fraction immediately to the left of 3/7
    """
    result: Fraction = Fraction(3, 7) - Fraction(1, 7 * (max_d // 7))
    if show_solution():
        difference = Fraction(3, 7) - result
        print(f'Solution for {max_d=}: {result=} {difference=} {result.numerator=}')
    return result.numerator


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(71))
