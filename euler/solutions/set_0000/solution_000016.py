#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 16: power_digit_sum

Problem Statement:
  2^{15} = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26. What is the
  sum of the digits of the number 2^{1000}?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=16
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=26,
        is_main_case=False,
        kwargs={'base': 2, 'power': 15},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1366,
        is_main_case=False,
        kwargs={'base': 2, 'power': 1000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #16
@register_solution(problem_number=16, test_cases=test_cases)
def power_digit_sum(*, base: int, power: int) -> int:
    """Calculate the sum of digits in the number base^power.

    This function computes the sum of individual digits in the number resulting from
    raising 'base' to the power of 'power'. The solution leverages Python's built-in
    support for arbitrary-precision integers, which automatically handles large numbers
    without overflow issues.

    Implementation Details:
    1. Calculate base^power using Python's exponentiation operator (**)
    2. Convert the result to a string to access individual digits
    3. Iterate through each character, convert back to integer, and sum

    The algorithm's efficiency depends on Python's internal implementation of large
    integer arithmetic and string conversion, but is generally very fast even for
    large powers.

    Args:
        power: The exponent to which the base is raised
        base: The base number to be raised to the specified power (default: 2)

    Returns:
        The sum of all individual digits in the resulting number

    Complexity:
        Time: O(log₁₀(base^power)) - proportional to the number of digits
        Space: O(log₁₀(base^power)) - for storing the string representation

    Examples:
        >>> power_digit_sum(power=15)  # 2^15 = 32768
        26  # 3+2+7+6+8 = 26

        >>> power_digit_sum(power=10, base=10)  # 10^10 = 10,000,000,000
        1  # Only one non-zero digit: 1+0+...+0 = 1
    """
    return sum(int(i) for i in str(base ** power))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(16))
