#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 34: digit_factorials

Problem Statement:
  145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145. Find the sum of
  all numbers which are equal to the sum of the factorial of their digits. Note:
  As 1! = 1 and 2! = 2 are not sums they are not included.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=34
Answer: None
"""
from __future__ import annotations

from itertools import combinations_with_replacement

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=40730,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #34
@register_solution(problem_number=34, test_cases=test_cases)
def digit_factorials() -> int:
    """Find the sum of all numbers equal to the sum of the factorials of their digits.

    This function identifies all numbers where the sum of the factorials of each digit
    equals the number itself. It excludes 1 and 2 as specified in the problem statement.

    Returns:
        The sum of all numbers that equal the sum of the factorials of their digits

    Example:
        >>> digit_factorials()
        40730  # Includes numbers like 145 (1! + 4! + 5! = 145)
    """
    upper_bound_num_digits = 7 + 1
    factorial = {'0': 1, '1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5040, '8': 40320, '9': 362880}
    return sum(
        int(num)
        for num_digits in range(2, upper_bound_num_digits)
        for digits in combinations_with_replacement('0123456789', num_digits)
        for num in (str(sum(factorial[d] for d in digits)),)
        if len(num) == num_digits
        and all(digit in num for digit in digits)
        and num == str(sum(factorial[n] for n in num))
    )


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(34))
