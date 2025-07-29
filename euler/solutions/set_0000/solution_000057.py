#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 57: square_root_convergents

Problem Statement:
  It is possible to show that the square root of two can be expressed as an
  infinite continued fraction. \sqrt 2 =1+ \frac 1 {2+ \frac 1 {2 +\frac 1 {2+
  ...}}} By expanding this for the first four iterations, we get: 1 + \frac 1 2 =
  \frac  32 = 1.5 1 + \frac 1 {2 + \frac 1 2} = \frac 7 5 = 1.4 1 + \frac 1 {2 +
  \frac 1 {2+\frac 1 2}} = \frac {17}{12} = 1.41666 ... 1 + \frac 1 {2 + \frac 1
  {2+\frac 1 {2+\frac 1 2}}} = \frac {41}{29} = 1.41379 ... The next three
  expansions are \frac {99}{70}, \frac {239}{169}, and \frac {577}{408}, but the
  eighth expansion, \frac {1393}{985}, is the first example where the number of
  digits in the numerator exceeds the number of digits in the denominator. In the
  first one-thousand expansions, how many fractions contain a numerator with more
  digits than the denominator?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=57
Answer: None
"""
from __future__ import annotations

from sys import set_int_max_str_digits

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=1,
        is_main_case=False,
        kwargs={'expansions': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=15,
        is_main_case=False,
        kwargs={'expansions': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=153,
        is_main_case=False,
        kwargs={'expansions': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1508,
        is_main_case=False,
        kwargs={'expansions': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #57
@register_solution(problem_number=57, test_cases=test_cases)
def square_root_convergents(*, expansions: int) -> int:
    """
    Count the fractions in the continued fraction expansion of √2 where the numerator
    has more digits than the denominator.

    This solution efficiently computes the convergents of the continued fraction expansion
    of √2 using a recurrence relation. For each expansion, we check if the numerator has
    more digits than the denominator and count those instances.

    Args:
        expansions: The number of expansions to compute

    Returns:
        The count of fractions where the numerator has more digits than the denominator

    Example:
        >>> square_root_convergents(expansions=1000)
        153
    """
    # Initialize variables for the recurrence relation
    # Starting with h_0=1, k_0=1 (representing 1/1)
    numerator, denominator, result = 1, 1, 0

    # Compute each expansion using the recurrence relation
    for _ in range(expansions):
        # Calculate the next convergent using the recurrence relation:
        # h_n = h_{n-1} + 2*k_{n-1}
        # k_n = h_{n-1} + k_{n-1}
        numerator, denominator = numerator + 2 * denominator, numerator + denominator

        # Check if the numerator has more digits than the denominator
        # Using boolean as integer (True = 1, False = 0) to increment result
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            # Handle potential integer string conversion limit in Python
            # This occurs with very large numbers
            set_int_max_str_digits(0)  # Disable the limit
            print(f'sys.set_int_max_str_digits(0) {expansions=}, {len(str(numerator))=}, {len(str(denominator))=}')
            result += len(str(numerator)) > len(str(denominator))

    # Return the total count of fractions meeting the criteria
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(57))
