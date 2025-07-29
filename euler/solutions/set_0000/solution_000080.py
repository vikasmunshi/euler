#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 80: square_root_digital_expansion

Problem Statement:
  It is well known that if the square root of a natural number is not an integer,
  then it is irrational. The decimal expansion of such square roots is infinite
  without any repeating pattern at all. The square root of two is
  1.41421356237309504880\cdots, and the digital sum of the first one hundred
  decimal digits is 475. For the first one hundred natural numbers, find the total
  of the digital sums of the first one hundred decimal digits for all the
  irrational square roots.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=80
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.sqrt import sqrt_binary_search, sqrt_heron_method
from euler.maths.sum_digits import sum_digits
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=475,
        is_main_case=False,
        kwargs={'digits': 100, 'max_num': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=40886,
        is_main_case=False,
        kwargs={'digits': 100, 'max_num': 99},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=434576,
        is_main_case=False,
        kwargs={'digits': 100, 'max_num': 999},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #80
@register_solution(problem_number=80, test_cases=test_cases)
def sol_1_square_root_digital_expansion(*, digits: int, max_num: int) -> int:
    """Calculate the sum of digits for irrational square roots using binary search.

    This function calculates the sum of the first 'digits' decimal digits
    for the square roots of all non-perfect-square numbers from 2 to max_num.
    It uses the binary search implementation from the euler.misc.sqrt module.

    Args:
        max_num: The maximum number to consider (inclusive)
        digits: The number of decimal digits to include in the calculation

    Returns:
        The sum of all digits across all irrational square roots

    Example:
        For max_num=2 and digits=100, the function returns 475, which is
        the sum of the first 100 digits of the square root of 2.

    Performance:
        The binary search method provides more consistent performance across
        different inputs compared to Heron's method, but is generally slower.
        It's included as an alternative implementation for validation and
        comparison purposes.
    """
    result: int = 0
    for i in range(2, max_num + 1):
        if (i ** 0.5) % 1 == 0:  # is a perfect square
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return result


# Register this function as a solution for problem #80
@register_solution(problem_number=80, test_cases=test_cases)
def sol_2_square_root_digital_expansion(*, digits: int, max_num: int) -> int:
    """Calculate the sum of digits for irrational square roots using Heron's method.

    This function calculates the sum of the first 'digits' decimal digits
    for the square roots of all non-perfect-square numbers from 2 to max_num.
    It uses the Heron's method implementation from the euler.misc.sqrt module.

    Args:
        max_num: The maximum number to consider (inclusive)
        digits: The number of decimal digits to include in the calculation

    Returns:
        The sum of all digits across all irrational square roots

    Example:
        For max_num=2 and digits=100, the function returns 475, which is
        the sum of the first 100 digits of the square root of 2.

    Performance:
        Heron's method typically converges quickly and is efficient for most inputs,
        making it the preferred implementation for this problem.
    """
    result: int = 0
    for i in range(2, max_num + 1):
        if (i ** 0.5) % 1 == 0:  # is a perfect square
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(80))
