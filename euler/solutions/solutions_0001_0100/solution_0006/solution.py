#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 6: Sum Square Difference.

  Problem Statement:
    The sum of the squares of the first ten natural numbers is,

    1^2 + 2^2 + ... + 10^2 = 385.

    The square of the sum of the first ten natural numbers is,

    (1 + 2 + ... + 10)^2 = 55^2 = 3025.

    Hence the difference between the sum of the squares of the first ten
    natural numbers and the square of the sum is 3025 - 385 = 2640.

    Find the difference between the sum of the squares of the first one
    hundred natural numbers and the square of the sum.

  Solution Approach:
    To solve this problem, consider the formulas for the sum of the first
    n natural numbers and the sum of the squares of the first n natural
    numbers. The sum of the first n numbers is n(n + 1)/2, and the sum of
    squares is n(n + 1)(2n + 1)/6. Compute the square of the sum using the
    first formula, then subtract the sum of the squares from it. Efficient
    computation can be done directly using these closed-form expressions,
    avoiding iteration and ensuring fast calculation even for large n.

  Test Cases:
    preliminary:
      n=10,
      answer=2640.

    main:
      n=100,
      answer=25164150.


  Answer: 25164150
  URL: https://projecteuler.net/problem=6
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=6, test_case_category=TestCaseCategory.EXTENDED)
def sum_square_difference(*, n: int) -> int:
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=6, time_out_in_seconds=300, mode='evaluate'))
