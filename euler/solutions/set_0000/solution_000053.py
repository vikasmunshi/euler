#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 53: combinatoric_selections

Problem Statement:
  There are exactly ten ways of selecting three from five, 12345: 123, 124, 125,
  134, 135, 145, 234, 235, 245, and 345 In combinatorics, we use the notation,
  \displaystyle \binom 5 3 = 10. In general, \displaystyle \binom n r =
  \dfrac{n!}{r!(n-r)!}, where r \le n, n! = n * (n-1) * ... * 3 * 2 * 1, and 0! =
  1.  It is not until n = 23, that a value exceeds one-million: \displaystyle
  \binom {23} {10} = 1144066. How many, not necessarily distinct, values of
  \displaystyle \binom n r for 1 \le n \le 100, are greater than one-million?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=53
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=4724,
        is_main_case=False,
        kwargs={'max_n': 100, 'threshold': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=4075,
        is_main_case=False,
        kwargs={'max_n': 100, 'threshold': 1000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=494861,
        is_main_case=False,
        kwargs={'max_n': 1000, 'threshold': 1000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=491894,
        is_main_case=False,
        kwargs={'max_n': 1000, 'threshold': 1000000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #53
@register_solution(problem_number=53, test_cases=test_cases)
def combinatoric_selections(*, max_n: int, threshold: int) -> int:
    """
    Count binomial coefficients C(n,r) that exceed a given threshold.

    This function efficiently computes the number of binomial coefficient values C(n,r)
    that are greater than the specified threshold, where n ranges from 1 to max_n.
    It uses mathematical properties of binomial coefficients to avoid unnecessary
    calculations.

    Args:
        max_n: Maximum value of n to consider (100 for the original problem)
        threshold: Value that binomial coefficients must exceed to be counted (10^6 for the original problem)

    Returns:
        Number of binomial coefficients greater than the threshold

    Examples:
        >>> combinatoric_selections(max_n=100, threshold=10**6)
        4075  # Answer to the original problem
        >>> combinatoric_selections(max_n=100, threshold=10**2)
        4724  # Different threshold for testing
    """
    count = 0
    for n in range(1, max_n + 1):
        c = 1  # Initialize C(n, 0) = 1 for all n
        for r in range(0, n // 2 + 1):  # Only compute up to n//2 due to symmetry: C(n,r) = C(n,n-r)
            if c > threshold:
                # When C(n,r) exceeds threshold, all remaining values C(n,r+1)...C(n,n/2) also exceed it
                # We count all these values plus their symmetric counterparts
                count += (n - 2 * r + 1)  # This formula counts all remaining values in the current row
                break
            else:
                # Use recursive formula to compute the next coefficient:
                # C(n,r+1) = C(n,r) * (n-r) / (r+1)
                c = c * (n - r) // (r + 1)
    return count


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(53))
