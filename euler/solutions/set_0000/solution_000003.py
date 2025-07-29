#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 3: largest_prime_factor

Problem Statement:
  The prime factors of 13195 are 5, 7, 13 and 29. What is the largest prime factor
  of the number 600851475143?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=3
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=29,
        is_main_case=False,
        kwargs={'number': 13195},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=6857,
        is_main_case=False,
        kwargs={'number': 600851475143},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #3
@register_solution(problem_number=3, test_cases=test_cases)
def largest_prime_factor(*, number: int) -> int:
    """Find the largest prime factor of a given number.

    This function uses a trial division algorithm to find prime factors.
    It handles even numbers separately for optimization, then checks only odd
    numbers. The search space is limited to the square root of the current number.

    Args:
        number: The number to find the largest prime factor of

    Returns:
        The largest prime factor of the input number

    Example:
        >>> largest_prime_factor(number=13195)
        29
        >>> largest_prime_factor(number=600851475143)
        6857
    """
    # Handle the smallest prime factor (2) separately for optimization
    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1

    # Initialize the potential factor and the search limit
    current_factor = 3
    search_limit = int(remaining_number ** 0.5)

    # Check odd factors up to the square root of the current number
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            # When a factor is found, reduce the number and update the largest factor
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            # Update the search limit based on the new reduced number
            search_limit = int(remaining_number ** 0.5)
        current_factor += 2  # Check only odd numbers

    # If remaining_number > 1, it is the largest prime factor
    # Otherwise, return the largest factor found so far
    return remaining_number if remaining_number > 1 else largest_factor


def reduce(num: int, divisor: int) -> int:
    """Reduce a number by dividing it by a divisor until it's no longer divisible.

    Args:
        num: The number to reduce
        divisor: The divisor to use for reduction

    Returns:
        The reduced number after removing all instances of the divisor

    Example:
        >>> reduce(48, 2) # 48 / 2^4 = 3
        3
        >>> reduce(45, 3) # 45 / 3^2 = 5
        5
    """
    # First division to ensure the num is at least divisible once by divisor
    num //= divisor

    # Continue dividing as long as possible
    while num % divisor == 0:
        num //= divisor

    return num


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(3))
