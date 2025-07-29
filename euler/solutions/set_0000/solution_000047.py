#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 47: distinct_primes_factors

Problem Statement:
  The first two consecutive numbers to have two distinct prime factors are:
  \begin{align} 14 &= 2 * 7\\ 15 &= 3 * 5. \end{align} The first three consecutive
  numbers to have three distinct prime factors are: \begin{align} 644 &= 2^2 * 7 *
  23\\ 645 &= 3 * 5 * 43\\ 646 &= 2 * 17 * 19. \end{align} Find the first four
  consecutive integers to have four distinct prime factors each. What is the first
  of these numbers?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=47
Answer: None
"""
from __future__ import annotations

from itertools import count

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import prime_factor_count
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=14,
        is_main_case=False,
        kwargs={'n': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=644,
        is_main_case=False,
        kwargs={'n': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=134043,
        is_main_case=False,
        kwargs={'n': 4},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #47
@register_solution(problem_number=47, test_cases=test_cases)
def distinct_primes_factors(*, n: int) -> int:
    """
    Find the first of n consecutive integers, each with exactly n distinct prime factors.

    This solution searches for sequences of consecutive integers with specific prime
    factorization properties. It efficiently iterates through integers and checks if
    each number in a consecutive sequence has exactly the required number of distinct
    prime factors.

    Args:
        n: The parameter defining both the length of the consecutive sequence and
           the number of distinct prime factors required for each integer

    Returns:
        The first integer in the sequence of n consecutive integers with the required property

    Examples:
        >>> distinct_primes_factors(2)  # First sequence with 2 factors each
        14              # 14=2×7 and 15=3×5
        >>> distinct_primes_factors(3)  # First sequence with 3 factors each
        644             # 644=2²×7×23, 645=3×5×43, 646=2×17×19
        >>> distinct_primes_factors(4)  # First sequence with 4 factors each
        134043          # The answer to the main problem
    """
    return next(number for number in count(2) if not any(prime_factor_count(number + i) != n for i in range(0, n)))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(47))
