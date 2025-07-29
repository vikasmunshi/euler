#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 70: totient_permutation

Problem Statement:
  Euler's totient function, \phi(n) [sometimes called the phi function], is used
  to determine the number of positive numbers less than or equal to n which are
  relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less than
  nine and relatively prime to nine, \phi(9)=6.The number 1 is considered to be
  relatively prime to every positive number, so \phi(1)=1.  Interestingly,
  \phi(87109)=79180, and it can be seen that 87109 is a permutation of 79180. Find
  the value of n, 1 \lt n \lt 10^7, for which \phi(n) is a permutation of n and
  the ratio n/\phi(n) produces a minimum.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=70
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sieve
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=8319823,
        is_main_case=False,
        kwargs={'n': 10000000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=99836521,
        is_main_case=False,
        kwargs={'n': 100000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #70
@register_solution(problem_number=70, test_cases=test_cases)
def totient_permutation(*, n: int) -> int:
    """
    Find the value of n < limit for which φ(n) is a permutation of n and n/φ(n) is minimized.

    The function searches for a number n that is a product of two primes p₁ and p₂,
    where the totient function φ(n) = (p₁-1)(p₂-1) forms a digit permutation of n,
    and the ratio n/φ(n) is minimized.

    Args:
        n: The upper limit for the search (exclusive)

    Returns:
        The value of n < limit for which φ(n) is a permutation of n and n/φ(n) is minimized

    Mathematical background:
    - For a product of two primes: φ(p₁×p₂) = (p₁-1)(p₂-1)
    - The ratio n/φ(n) = (p₁×p₂)/((p₁-1)(p₂-1)) approaches 1 as p₁ and p₂ increase
    - We focus on primes near √n for efficiency
    """
    min_ratio: float = float('inf')  # Initialize with infinity to find minimum
    min_n: int = 0  # The number with the minimum ratio
    sqrt_n = int(n ** 0.5)  # Square root of the limit

    # Set search boundaries for the first prime
    # We start from sqrt(n)/2 to focus on larger primes for a smaller ratio
    min_prime_1, max_prime_1 = sqrt_n // 2, sqrt_n

    for prime_1 in (p for p in gen_primes_sieve() if p > min_prime_1):
        # Exit if we've exceeded our maximum for the first prime
        if prime_1 > max_prime_1:
            break

        # Calculate bounds for the second prime
        # The second prime must be at least prime_1+2 (ensuring different primes)
        # and at most n/prime_1 (ensuring their product is less than n)
        min_prime_2, max_prime_2 = prime_1 + 2, int(n / prime_1)

        for prime_2 in (p for p in gen_primes_sieve() if p > min_prime_2):
            # Exit inner loop if second prime exceeds its maximum
            if prime_2 > max_prime_2:
                break

            # Calculate the number (product of primes) and its totient value
            # Using assignment expressions (:=) for concise code
            # Check if number and totient are permutations of each other by sorting their digits and comparing
            if sorted(str(number := prime_1 * prime_2)) == sorted(str(totient := (prime_1 - 1) * (prime_2 - 1))):
                # Calculate the ratio and update if it's smaller than the current minimum
                if (ratio := number / totient) < min_ratio:
                    min_ratio, min_n = ratio, number
    return min_n


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(70))
