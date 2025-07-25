#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 53: Combinatoric selections

Problem Statement:
There are exactly ten ways of selecting three from five, 12345:
123, 124, 125, 134, 135, 145, 234, 235, 245, and 345

In combinatorics, we use the notation, C(5,3) = 10.

In general, C(n,r) = n!/(r!(n-r)!), where:
- r ≤ n
- n! = n × (n-1) × ... × 3 × 2 × 1
- 0! = 1

It is not until n = 23, that a value exceeds one-million: C(23,10) = 1,144,066.

How many, not necessarily distinct, values of C(n,r) for 1 ≤ n ≤ 100, are greater
than one-million?

Solution Approach:
This solution efficiently counts binomial coefficients exceeding a threshold by using:

1. The symmetry property of binomial coefficients: C(n,r) = C(n,n-r)
2. A recursive formula to compute each coefficient: C(n,r+1) = C(n,r) × (n-r)/(r+1)
3. Early termination when the threshold is exceeded, using the fact that once a
   coefficient exceeds the threshold, all remaining values in that row will also exceed it

For each value of n from 1 to max_n, the algorithm:
- Starts with C(n,0) = 1
- Computes coefficients C(n,r) for increasing r
- When a coefficient exceeds the threshold, counts all remaining values in that row
  without explicitly computing them

Test Cases:
- For max_n=100, threshold=100: 4724 values exceed threshold
- For max_n=100, threshold=1,000,000: 4075 values exceed threshold (the answer)
- For max_n=1000, threshold=1,000,000: 494861 values exceed threshold

URL: https://projecteuler.net/problem=53
Answer: 4075
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=53)
problem_number: int = 53

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_n': 100, 'threshold': 10 ** 2}, answer=4724, ),
    ProblemArgs(kwargs={'max_n': 100, 'threshold': 10 ** 6}, answer=4075, ),
    ProblemArgs(kwargs={'max_n': 1000, 'threshold': 10 ** 6}, answer=494861, ),
    ProblemArgs(kwargs={'max_n': 1000, 'threshold': 10 ** 9}, answer=491894, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_binomial_coefficients_greater_than_threshold(*, max_n: int, threshold: int) -> int:
    """
    Count binomial coefficients C(n,r) that exceed a given threshold.

    This function efficiently computes the number of binomial coefficient values C(n,r)
    that are greater than the specified threshold, where n ranges from 1 to max_n.
    It uses mathematical properties of binomial coefficients to avoid unnecessary
    calculations.

    Args:
        max_n: Maximum value of n to consider (100 for the original problem)
        threshold: Value that binomial coefficients must exceed to be counted (10^6 for the original problem)

    Returns:
        Number of binomial coefficients greater than the threshold

    Examples:
        >>> count_binomial_coefficients_greater_than_threshold(max_n=100, threshold=10**6)
        4075  # Answer to the original problem
        >>> count_binomial_coefficients_greater_than_threshold(max_n=100, threshold=10**2)
        4724  # Different threshold for testing
    """
    count = 0
    for n in range(1, max_n + 1):
        c = 1  # Initialize C(n, 0) = 1 for all n
        for r in range(0, n // 2 + 1):  # Only compute up to n//2 due to symmetry: C(n,r) = C(n,n-r)
            if c > threshold:
                # When C(n,r) exceeds threshold, all remaining values C(n,r+1)...C(n,n/2) also exceed it
                # We count all these values plus their symmetric counterparts
                count += (n - 2 * r + 1)  # This formula counts all remaining values in the current row
                break
            else:
                # Use recursive formula to compute the next coefficient:
                # C(n,r+1) = C(n,r) * (n-r) / (r+1)
                c = c * (n - r) // (r + 1)
    return count


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
