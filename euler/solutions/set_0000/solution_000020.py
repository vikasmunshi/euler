#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 20: factorial_digit_sum

Problem Statement:
  n! means n * (n - 1) * \cdots * 3 * 2 * 1. For example, 10! = 10 * 9 * \cdots *
  3 * 2 * 1 = 3628800,and the sum of the digits in the number 10! is 3 + 6 + 2 + 8
  + 8 + 0 + 0 = 27. Find the sum of the digits in the number 100!.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=20
Answer: None
"""
from __future__ import annotations

from math import factorial

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=27,
        is_main_case=False,
        kwargs={'n': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=648,
        is_main_case=False,
        kwargs={'n': 100},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #20
@register_solution(problem_number=20, test_cases=test_cases)
def factorial_digit_sum(*, n: int) -> int:
    """Calculate the sum of digits in the factorial of a number.

    This function leverages Python's built-in factorial function from the math module,
    which can handle large integers. The resulting number is converted to a string
    to easily access and sum its individual digits.

    Implementation Details:
    1. Calculate n! using math.factorial(), which handles arbitrary-precision arithmetic
    2. Convert the result to a string representation
    3. Iterate through each character (digit), convert back to integer, and sum

    Python's ability to handle arbitrary-precision integers is crucial here, as factorial
    values grow extremely quickly. For example, 100! has 158 digits, far exceeding the
    capacity of fixed-size integer types in many programming languages.

    Complexity Analysis:
    - Time Complexity: O(n + d) where n is the input number (for factorial calculation)
      and d is the number of digits in n! (for the digit sum)
    - Space Complexity: O(d) for storing the string representation of the factorial

    Note that d, the number of digits in n!, grows approximately as O(n log n) according
    to Stirling's approximation, so the overall complexity is dominated by this term
    for large values of n.

    Args:
        n: A positive integer whose factorial's digits will be summed

    Returns:
        The sum of all digits in n!

    Examples:
        >>> factorial_digit_sum(10)  # 10! = 3,628,800
        27  # 3+6+2+8+8+0+0 = 27

        >>> factorial_digit_sum(5)  # 5! = 120
        3  # 1+2+0 = 3
    """
    return sum(int(d) for d in str(factorial(n)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(20))
