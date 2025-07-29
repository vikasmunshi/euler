#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 27: quadratic_primes

Problem Statement:
  Euler discovered the remarkable quadratic formula: n^2 + n + 41 It turns out
  that the formula will produce 40 primes for the consecutive integer values 0 \le
  n \le 39. However, when n = 40, 40^2 + 40 + 41 = 40(40 + 1) + 41 is divisible by
  41, and certainly when n = 41, 41^2 + 41 + 41 is clearly divisible by 41. The
  incredible formula n^2 - 79n + 1601 was discovered, which produces 80 primes for
  the consecutive values 0 \le n \le 79. The product of the coefficients, -79 and
  1601, is -126479. Considering quadratics of the form:  n^2 + an + b, where |a| <
  1000 and |b| \le 1000where |n| is the modulus/absolute value of ne.g. |11| = 11
  and |-4| = 4  Find the product of the coefficients, a and b, for the quadratic
  expression that produces the maximum number of primes for consecutive values of
  n, starting with n = 0.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=27
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sundaram_sieve, is_prime
from euler.setup import TestCase


def prime_run(a: int, b: int) -> int:
    """
    Calculate the number of consecutive primes produced by the quadratic formula n² + an + b.

    This function computes how many consecutive integers, starting from n=0,
    will produce prime numbers when substituted into the quadratic formula n² + an + b.

    Args:
        a: The coefficient of the linear term in the quadratic formula
        b: The constant term in the quadratic formula

    Returns:
        The count of consecutive primes generated starting from n=0

    Examples:
        >>> prime_run(1, 41)  # For n²+n+41
        40
        >>> prime_run(-79, 1601)  # For n²-79n+1601
        80
    """
    x = 0
    while is_prime(abs(x ** 2 + a * x + b)):
        x += 1
    return x


test_cases: list[TestCase] = [
    TestCase(
        answer=-59231,
        is_main_case=False,
        kwargs={'max_limit': 1000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #27
@register_solution(problem_number=27, test_cases=test_cases)
def quadratic_primes(*, max_limit: int) -> int:
    """
    Find the product of coefficients a and b that produces the maximum number of
    consecutive primes in the quadratic formula n² + an + b.

    This solution examines various coefficient combinations to find the quadratic
    formula that generates the longest sequence of prime numbers for consecutive
    values of n starting from 0.

    Args:
        max_limit: The maximum absolute value for coefficients a and b

    Returns:
        The product of the coefficients a and b that produces the maximum number
        of consecutive primes

    Example:
        >>> quadratic_primes(max_limit=1000)
        -59231  # The product of coefficients that produces the longest prime sequence
    """
    return max([
        max((prime_run(a, b), a * b),  # Test (a, b) combination
            (prime_run(a, -b), -a * b),  # Test (a, -b) combination
            (prime_run(-a, -b), a * b),  # Test (-a, -b) combination
            (prime_run(-a, b), -a * b))  # Test (-a, b) combination
        for b in gen_primes_sundaram_sieve(max_limit=max_limit)  # b must be prime
        for a in range(0 if b == 2 else 1, max_limit, 2)  # a should be odd (or 0 when b=2)
    ])[1]  # Return the product of coefficients (second element of tuple)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(27))
