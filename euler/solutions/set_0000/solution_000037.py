#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 37: truncatable_primes

Problem Statement:
  The number 3797 has an interesting property. Being prime itself, it is possible
  to continuously remove digits from left to right, and remain prime at each
  stage: 3797, 797, 97, and 7. Similarly we can work from right to left: 3797,
  379, 37, and 3. Find the sum of the only eleven primes that are both truncatable
  from left to right and right to left. NOTE: 2, 3, 5, and 7 are not considered to
  be truncatable primes.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=37
Answer: None
"""
from __future__ import annotations

from typing import List, Set

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sieve
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=748317,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #37
@register_solution(problem_number=37, test_cases=test_cases)
def truncatable_primes() -> int:
    """
    Find the sum of all truncatable primes, which remain prime when digits are removed.

    A truncatable prime is a prime number that remains prime after any digit is
    removed from left to right or right to left. For example, 3797 is truncatable
    because all of 3797, 797, 97, 7 (left truncation) and 3797, 379, 37, 3 (right
    truncation) are prime. The problem states there are exactly 11 such primes.

    Returns:
        The sum of all 11 truncatable primes

    Example:
        >>> truncatable_primes()
        748317
    """
    primes: Set[str] = set()  # Set of all primes encountered so far (as strings)
    truncatable_primes: List[int] = list()  # List to collect truncatable primes

    # Generate primes and check for truncatable property
    for prime_num in gen_primes_sieve():
        prime = str(prime_num)
        primes.add(prime)  # Add current prime to our set

        # Skip single-digit primes (as specified in the problem)
        if int(prime) < 10:
            continue

        # Check if all truncations are prime
        # Generate all left and right truncations and verify they're all prime
        # Left truncation: prime[i:] (e.g., 3797 → 797 → 97 → 7)
        # Right truncation: prime[:i] (e.g., 3797 → 379 → 37 → 3)
        if not any(pl not in primes or pr not in primes
                   for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))]):
            truncatable_primes.append(prime_num)

        # We only need to find 11 truncatable primes (as stated in the problem)
        if len(truncatable_primes) == 11:
            break

    # Return the sum of all truncatable primes
    return sum(truncatable_primes)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(37))
