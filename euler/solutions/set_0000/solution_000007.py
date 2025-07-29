#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 7: solution_10_001st_prime

Problem Statement:
  By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that
  the 6th prime is 13. What is the 10\,001st prime number?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=7
Answer: None
"""
from __future__ import annotations

from math import log

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=13,
        is_main_case=False,
        kwargs={'n': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=104743,
        is_main_case=False,
        kwargs={'n': 10001},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #7
@register_solution(problem_number=7, test_cases=test_cases)
def solution_10_001st_prime(*, n: int) -> int:
    """
    Find the nth prime number.

    This implementation uses a modified Sieve of Eratosthenes optimized for finding
    the nth prime number. It specifically focuses on odd numbers, since all even numbers
    except 2 are composite.

    Args:
        n: The position of the prime number to find (e.g., n=6 finds the 6th prime)

    Returns:
        The nth prime number

    Note:
        - For n=1, we return 2 (the first prime number) as a special case
        - For n>1, we search through odd numbers using the sieve method
        - The formula i+j+(2*i*j) generates indices of composite numbers
    """
    # Handle special case: the first prime number is 2
    if n == 1:
        return 2

    # Estimate the upper bound for the nth prime using Prime Number Theorem
    max_expected_value = int(n * log(n))

    # Initialize the sieve array where index i corresponds to number 2i+1
    numbers = list(range(0, max_expected_value + 1))

    # Apply the sieve algorithm to mark composite numbers
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not prime as 0
            except IndexError:
                break

    # Extract all non-zero values (representing prime indices)
    # Convert back to actual prime numbers using the formula 2i+1
    # Select the (n-2)th element (accounting for the fact that we've excluded 2,
    # and our indexing starts at 0)
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(7))
