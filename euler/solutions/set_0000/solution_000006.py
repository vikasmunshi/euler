#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 6: sum_square_difference

Problem Statement:
  The sum of the squares of the first ten natural numbers is, 1^2 + 2^2 + ... +
  10^2 = 385. The square of the sum of the first ten natural numbers is, (1 + 2 +
  ... + 10)^2 = 55^2 = 3025. Hence the difference between the sum of the squares
  of the first ten natural numbers and the square of the sum is 3025 - 385 = 2640.
  Find the difference between the sum of the squares of the first one hundred
  natural numbers and the square of the sum.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=6
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=2640,
        is_main_case=False,
        kwargs={'n': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=25164150,
        is_main_case=False,
        kwargs={'n': 100},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #6
@register_solution(problem_number=6, test_cases=test_cases)
def sum_square_difference(*, n: int) -> int:
    """
    Computes the difference between the square of the sum of the first `n`
    natural numbers and the sum of the squares of the first `n` natural numbers.

    Args:
        n (int): The number up to which the calculations are performed.

    Returns:
        int: The difference between the square of the sum and the sum of the squares.

    Explanation:
    - The sum of the first `n` natural numbers is calculated as:
      S = (n * (n + 1) // 2)
    - The square of the sum is:
      S^2
    - The sum of the squares of the first `n` natural numbers is calculated as:
      Sum of squares = (2 * n + 1) * (n + 1) * n // 6
    - Finally, the difference is:
      S^2 - Sum of squares
    """
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(6))
