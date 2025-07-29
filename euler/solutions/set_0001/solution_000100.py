#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 100: arranged_probability

Problem Statement:
  If a box contains twenty-one coloured discs, composed of fifteen blue discs and
  six red discs, and two discs were taken at random, it can be seen that the
  probability of taking two blue discs, P(\text{BB}) = (15/21) * (14/20) = 1/2.
  The next such arrangement, for which there is exactly 50\% chance of taking two
  blue discs at random, is a box containing eighty-five blue discs and thirty-five
  red discs. By finding the first arrangement to contain over 10^{12} =
  1\,000\,000\,000\,000 discs in total, determine the number of blue discs that
  the box would contain.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=100
Answer: 756872327473
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=15,
        is_main_case=False,
        kwargs={'total_discs': 21},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=85,
        is_main_case=False,
        kwargs={'total_discs': 120},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=756872327473,
        is_main_case=True,
        kwargs={'total_discs': 1000000000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #100
@register_solution(problem_number=100, test_cases=test_cases)
def arranged_probability(*, total_discs: int) -> int:
    """
    Calculate the number of blue discs needed for a probability of 1/2 when drawing two blue discs.

    The problem requires solving the equation: b/n * (b-1)/(n-1) = 1/2
    This can be transformed into a negative Pell equation: y² - 2x² = -1
    where y = 2b - 1 and x = 2n - 1

    Args:
        total_discs: The minimum total number of discs required

    Returns:
        The number of blue discs in the first valid arrangement with at least total_discs discs
    """
    # Initial solution to the negative Pell equation y² - 2x² = -1
    x, y = 1, 1
    # Generate solutions using recurrence relations
    while True:
        # Calculate next solution using recurrence formula
        x, y = 3 * x + 4 * y, 2 * x + 3 * y

        # Convert back to n and b
        n = (x + 1) // 2
        b = (y + 1) // 2

        # Check if we found a solution with total_discs > 10^12
        if n >= total_discs:
            return b


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(100))
