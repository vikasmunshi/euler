#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 30: digit_fifth_powers

Problem Statement:
  Surprisingly there are only three numbers that can be written as the sum of
  fourth powers of their digits: \begin{align} 1634 &= 1^4 + 6^4 + 3^4 + 4^4\\
  8208 &= 8^4 + 2^4 + 0^4 + 8^4\\ 9474 &= 9^4 + 4^4 + 7^4 + 4^4 \end{align} As 1 =
  1^4 is not a sum it is not included. The sum of these numbers is 1634 + 8208 +
  9474 = 19316. Find the sum of all the numbers that can be written as the sum of
  fifth powers of their digits.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=30
Answer: None
"""
from __future__ import annotations

from itertools import combinations_with_replacement
from math import ceil, log

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=19316,
        is_main_case=False,
        kwargs={'n': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=443839,
        is_main_case=False,
        kwargs={'n': 5},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #30
@register_solution(problem_number=30, test_cases=test_cases)
def digit_fifth_powers(*, n: int) -> int:
    """Calculate the sum of all numbers that equal the sum of nth powers of their digits.

    This function finds all numbers where the sum of the nth powers of their digits
    equals the number itself, then returns the sum of all such numbers.

    Args:
        n: The power to which each digit is raised

    Returns:
        The sum of all numbers that can be written as the sum of the nth powers of their digits

    Example:
        >>> digit_fifth_powers(n=4)
        19316  # Sum of 1634, 8208, and 9474
        >>> digit_fifth_powers(n=5)
        443839
    """
    upper_bound_num_digits = ceil(log(n * 9 ** n, 10))
    return sum(num for digits in combinations_with_replacement(range(10), upper_bound_num_digits)
               if (num := sum(x ** n for x in digits)) > 9 and num == sum(int(x) ** n for x in str(num)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(30))
