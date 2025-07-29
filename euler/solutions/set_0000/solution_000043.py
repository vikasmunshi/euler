#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 43: sub_string_divisibility

Problem Statement:
  The number, 1406357289, is a 0 to 9 pandigital number because it is made up of
  each of the digits 0 to 9 in some order, but it also has a rather interesting
  sub-string divisibility property. Let d_1 be the 1st digit, d_2 be the 2nd
  digit, and so on. In this way, we note the following: d_2d_3d_4=406 is divisible
  by 2 d_3d_4d_5=063 is divisible by 3 d_4d_5d_6=635 is divisible by 5
  d_5d_6d_7=357 is divisible by 7 d_6d_7d_8=572 is divisible by 11 d_7d_8d_9=728
  is divisible by 13 d_8d_9d_{10}=289 is divisible by 17 Find the sum of all 0 to
  9 pandigital numbers with this property.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=43
Answer: None
"""
from __future__ import annotations

from itertools import permutations
from typing import Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=16695334890,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #43
@register_solution(problem_number=43, test_cases=test_cases)
def sub_string_divisibility() -> int:
    """
    Find the sum of all 0-9 pandigital numbers with special divisibility properties.

    This solution finds pandigital numbers (using all digits 0-9 exactly once) where
    consecutive 3-digit substrings have specific divisibility properties. The approach
    generates permutations and filters them by the divisibility requirements specified
    in the problem.

    Returns:
        The sum of all 0-9 pandigital numbers with the required substring divisibility

    Example:
        >>> sub_string_divisibility()
        16695334890

    Note:
        The example number 1406357289 is included in the sum as it satisfies all constraints:
        - 406 is divisible by 2
        - 063 is divisible by 3
        - 635 is divisible by 5
        - 357 is divisible by 7
        - 572 is divisible by 11
        - 728 is divisible by 13
        - 289 is divisible by 17
    """
    divisors: Tuple[int, int, int, int, int, int, int] = (2, 3, 5, 7, 11, 13, 17)
    return sum(int(''.join(num_s)) for num_s in permutations('0123456789')
               if num_s[0] != '0'  # Skip numbers starting with 0
               and not any(int(''.join(num_s[i:i + 3])) % divisor != 0 for i, divisor in enumerate(divisors, start=1)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(43))
