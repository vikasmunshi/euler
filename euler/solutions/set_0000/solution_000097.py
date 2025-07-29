#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 97: large_non_mersenne_prime

Problem Statement:
  The first known prime found to exceed one million digits was discovered in 1999,
  and is a Mersenne prime of the form 2^{6972593} - 1; it contains exactly
  2\,098\,960 digits. Subsequently other Mersenne primes, of the form 2^p - 1,
  have been found which contain more digits. However, in 2004 there was found a
  massive non-Mersenne prime which contains 2\,357\,207 digits: 28433 *
  2^{7830457} + 1. Find the last ten digits of this prime number.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=97
Answer: None
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=8739992577,
        is_main_case=False,
        kwargs={'num_digits': 10, 'prime': '28433 × 2^7830457 + 1'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #97
@register_solution(problem_number=97, test_cases=test_cases)
def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    """
    Calculate the last n digits of a large prime number of form 'a × 2^b + 1'.

    This function efficiently computes the last digits of a large number without
    calculating the entire number, using modular arithmetic properties. For each
    step of the exponentiation, we only need to keep track of the remainder when
    divided by 10^num_digits.

    Args:
        prime: String representation of the prime in the format 'a × 2^b + 1'
        num_digits: Number of last digits to calculate (e.g., 10 for last ten digits)

    Returns:
        int: The last num_digits digits of the calculated prime number

    Example:
        large_non_mersenne_prime(prime='28433 × 2^7830457 + 1', num_digits=10) -> 8739992577
    """
    # Calculate 10^num_digits, which will be used as the modulus
    divisor: int = 10 ** num_digits

    # Parse the prime formula from the string representation
    prime_parts: List[str] = prime.split()
    number: int
    exponent: int
    number, exponent = int(prime_parts[0]), int(prime_parts[2][2:])  # Extract coefficient and exponent

    # Calculate (number * 2^exponent) % divisor using iterative approach
    # This is more efficient than calculating the full power first
    # Note: For even larger exponents, a binary exponentiation algorithm (square-and-multiply)
    # would be more efficient with O(log n) complexity instead of O(n)
    for _ in range(exponent):
        number *= 2
        number %= divisor  # Take modulus at each step to keep the number manageable

    # Add 1 and take modulus again for the final result
    number += 1
    number %= divisor

    return number


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(97))
