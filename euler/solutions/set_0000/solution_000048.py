#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 48: self_powers

Problem Statement:
  The series, 1^1 + 2^2 + 3^3 + \cdots + 10^{10} = 10405071317. Find the last ten
  digits of the series, 1^1 + 2^2 + 3^3 + \cdots + 1000^{1000}.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=48
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=405071317,
        is_main_case=False,
        kwargs={'n': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9027641920,
        is_main_case=False,
        kwargs={'n': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9110846700,
        is_main_case=False,
        kwargs={'n': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=6237204500,
        is_main_case=False,
        kwargs={'n': 10000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=3031782500,
        is_main_case=False,
        kwargs={'n': 100000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=4077562500,
        is_main_case=False,
        kwargs={'n': 1000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #48
@register_solution(problem_number=48, test_cases=test_cases)
def self_powers(*, n: int) -> int:
    """
    # Note: For extremely large values of n, this computation could be parallelized
    # by splitting the range into chunks and processing them concurrently, then combining
    # the results. However, for the given constraints (n ≤ 10000), the sequential
    # approach is already efficient.
    Calculate the last ten digits of the sum of self-powers series.

    This function computes the sum of the series 1¹ + 2² + 3³ + ... + n^n and returns
    only the last ten digits by applying modulo 10¹⁰ throughout the calculation.

    The implementation uses Python's built-in pow() function with the modulo argument
    for efficient modular exponentiation, which is significantly faster than the naive
    approach of calculating the full i^i value for large values of i.

    Args:
        n: The upper limit of the series (inclusive)

    Returns:
        The last ten digits of the sum

    Examples:
        >>> self_powers(n=10)
        405071317  # Last 10 digits of 10,405,071,317
        >>> self_powers(n=100)
        9027641920
        >>> self_powers(n=1000)
        9110846700  # The answer to the main problem
    """
    modulo: int = 10 ** 10  # last 10 digits
    result: int = 0

    # Since there's no closed formula for the sum of i^i series,
    # we need to compute each term, but we can optimize using modular exponentiation
    for i in range(1, n + 1):
        # Calculate i^i mod 10^10 efficiently using modular exponentiation
        # This is more efficient for large values of i than direct computation
        term = pow(i, i, modulo)
        result = (result + term) % modulo
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(48))
