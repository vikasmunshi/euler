#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 25: solution_1000_digit_fibonacci_number

Problem Statement:
  The Fibonacci sequence is defined by the recurrence relation: F_n = F_{n - 1} +
  F_{n - 2}, where F_1 = 1 and F_2 = 1. Hence the first 12 terms will be:
  \begin{align} F_1 &= 1\\ F_2 &= 1\\ F_3 &= 2\\ F_4 &= 3\\ F_5 &= 5\\ F_6 &= 8\\
  F_7 &= 13\\ F_8 &= 21\\ F_9 &= 34\\ F_{10} &= 55\\ F_{11} &= 89\\ F_{12} &= 144
  \end{align} The 12th term, F_{12}, is the first term to contain three digits.
  What is the index of the first term in the Fibonacci sequence to contain 1000
  digits?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=25
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=12,
        is_main_case=False,
        kwargs={'n': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=4782,
        is_main_case=False,
        kwargs={'n': 1000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #25
@register_solution(problem_number=25, test_cases=test_cases)
def solution_1000_digit_fibonacci_number(*, n: int) -> int:
    """
    Find the index of the first Fibonacci number with n digits.

    This solution iteratively generates Fibonacci numbers using the recurrence relation
    F_n = F_{n-1} + F_{n-2}, starting with F_1 = F_2 = 1. It continues until finding the
    first number with at least n digits, determined by checking if the number is greater
    than or equal to 10^(n-1).

    Args:
        n: The number of digits to look for in a Fibonacci number

    Returns:
        The index (1-based) of the first Fibonacci number with n digits

    Example:
        >>> solution_1000_digit_fibonacci_number(n=3)
        12  # F_12 = 144 is the first Fibonacci number with 3 digits
        >>> solution_1000_digit_fibonacci_number(n=1000)
        4782  # The answer to the original problem
    """
    a, b = 1, 1
    i = 2
    while b < 10 ** (n - 1):
        a, b = b, a + b
        i += 1
    return i


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(25))
