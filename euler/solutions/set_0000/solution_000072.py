#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 72: counting_fractions

Problem Statement:
  Consider the fraction, \dfrac n d, where n and d are positive integers. If n \lt
  d and \operatorname{HCF}(n,d)=1, it is called a reduced proper fraction. If we
  list the set of reduced proper fractions for d \le 8 in ascending order of size,
  we get: \frac 1 8, \frac 1 7, \frac 1 6, \frac 1 5, \frac 1 4, \frac 2 7, \frac
  1 3, \frac 3 8, \frac 2 5, \frac 3 7, \frac 1 2, \frac 4 7, \frac 3 5, \frac 5
  8, \frac 2 3, \frac 5 7, \frac 3 4, \frac 4 5, \frac 5 6, \frac 6 7, \frac 7 8
  It can be seen that there are 21 elements in this set. How many elements would
  be contained in the set of reduced proper fractions for d \le 1\,000\,000?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=72
Answer: None
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=21,
        is_main_case=False,
        kwargs={'max_d': 8},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=31,
        is_main_case=False,
        kwargs={'max_d': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=3043,
        is_main_case=False,
        kwargs={'max_d': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=304191,
        is_main_case=False,
        kwargs={'max_d': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=30397485,
        is_main_case=False,
        kwargs={'max_d': 10000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=3039650753,
        is_main_case=False,
        kwargs={'max_d': 100000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=303963552391,
        is_main_case=False,
        kwargs={'max_d': 1000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=30396356427241,
        is_main_case=False,
        kwargs={'max_d': 10000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #72
@register_solution(problem_number=72, test_cases=test_cases)
def counting_fractions(*, max_d: int) -> int:
    """
    Calculate the total number of reduced proper fractions for denominators less than max_d.

    Args:
        max_d: The upper limit for denominators (exclusive)

    Returns:
        The count of all reduced proper fractions with denominators less than max_d
    """
    # Initialize the totient array with values from 0 to max_d
    # Each number starts as its own value before applying Euler's totient function
    euler_totients: List[int] = list(range(max_d + 1))

    # Apply the sieve method to calculate totients
    # For each prime p, multiply numbers containing p by (p-1)/p
    for n in range(2, max_d + 1):
        if euler_totients[n] == n:  # n is prime (unchanged from the initial value)
            for j in range(n, max_d + 1, n):
                # Update totient: multiply by (p-1)/p for each prime factor
                euler_totients[j] = (euler_totients[j] // n) * (n - 1)
    return sum(euler_totients[d] for d in range(2, max_d + 1))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(72))
