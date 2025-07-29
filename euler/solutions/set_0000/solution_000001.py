#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 1: multiples_of_3_or_5

Problem Statement:
  If we list all the natural numbers below 10 that are multiples of 3 or 5, we get
  3, 5, 6 and 9. The sum of these multiples is 23. Find the sum of all the
  multiples of 3 or 5 below 1000.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=1
Answer: 233168
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=23,
        is_main_case=False,
        kwargs={'max_limit': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=233168,
        is_main_case=True,
        kwargs={'max_limit': 1000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #1
@register_solution(problem_number=1, test_cases=test_cases)
def multiples_of_3_or_5(*, max_limit: int) -> int:
    """
    This solution uses the arithmetic sum formula to efficiently calculate
    the sum of multiples without iterating through each number. It applies
    the inclusion-exclusion principle to avoid double-counting numbers that
    are multiples of both 3 and 5 (i.e., multiples of 15).

    Args:
        max_limit (int):

    Returns:
        The sum of all multiples of 3 or 5 below max_limit

    Example:
        >>> multiples_of_3_and_5(max_limit=10)
        23
        >>> multiples_of_3_and_5(max_limit=1000)
        233,168
    """

    def sum_multiples(number: int) -> int:
        """Calculate the sum of multiples of 'number' up-to max_limit using formula for arithmetic sum: n(n+1)/2."""
        terms = (max_limit - 1) // number
        return number * terms * (terms + 1) // 2

    # Apply inclusion-exclusion principle:
    # sum(multiples of 3) + sum(multiples of 5) - sum(multiples of 15)
    return sum_multiples(3) + sum_multiples(5) - sum_multiples(3 * 5)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(1))
