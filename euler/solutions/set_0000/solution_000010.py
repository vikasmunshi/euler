#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 10: summation_of_primes

Problem Statement:
  The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17. Find the sum of all the
  primes below two million.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=10
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sundaram_sieve
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=17,
        is_main_case=False,
        kwargs={'max_num': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=142913828922,
        is_main_case=False,
        kwargs={'max_num': 2000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #10
@register_solution(problem_number=10, test_cases=test_cases)
def summation_of_primes(*, max_num: int) -> int:
    """
    Calculate the sum of all prime numbers below a given limit.

    This function generates all prime numbers below the specified limit using the
    Sieve of Sundaram algorithm, then calculates their sum.

    Args:
        max_num: The upper limit (exclusive) for prime numbers to include in the sum

    Returns:
        The sum of all prime numbers less than max_num

    Examples:
        >>> summation_of_primes(max_num=10)
        17  # Sum of 2, 3, 5, and 7
        >>> summation_of_primes(max_num=2000000)
        142913828922

    Time Complexity: O(n log log n) where n is max_num, due to the sieve algorithm
    Space Complexity: O(n) for storing the prime numbers
    """
    return sum(gen_primes_sundaram_sieve(max_limit=max_num))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(10))
