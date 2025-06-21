# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 53
# https://projecteuler.net/problem=53
# Answer: 4075
# Notes:
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_n': 100, 'threshold': 10 ** 2}, answer=4724, ),
    ProblemArgs(kwargs={'max_n': 100, 'threshold': 10 ** 6}, answer=4075, ),
    ProblemArgs(kwargs={'max_n': 1000, 'threshold': 10 ** 6}, answer=494861, ),
    ProblemArgs(kwargs={'max_n': 1000, 'threshold': 10 ** 9}, answer=491894, ),
]


def solution(*, max_n: int, threshold: int) -> int:
    """
    Solution to Project Euler problem 53: Combinatoric selections
    https://projecteuler.net/problem=53

    Problem Description:
    There are exactly ten ways of selecting three from five, 12345:
    123, 124, 125, 134, 135, 145, 234, 235, 245, and 345

    In combinatorics, we use the notation: binom{5}{3} = 10.

    In general, binom{n}{r} = n! // (r! * (n-r)!), where:
    - r <= n
    - n! = n * (n-1) * ... * 3 * 2 * 1
    - 0! = 1

    It is not until n = 23 that a value exceeds one-million: binom{23}{10} = 1,144,066.

    Problem Statement:
    How many, not necessarily distinct, values of binom{n}{r} for 1 <= n <= 100,
    are greater than one-million?

    Solution Approach:
    Determine the count of binomial coefficients greater than a given threshold.

    This function computes the number of binomial coefficient values C(n, r) that
    are greater than a specified threshold, where n ranges from 1 to `max_n`.
    
    Key optimizations:
    1. Leverages symmetry of binomial coefficients: C(n, r) = C(n, n-r)
    2. Uses a recursive formula to efficiently compute each coefficient:
       C(n, r+1) = C(n, r) * (n-r) / (r+1)
    3. Employs early termination when the threshold is exceeded, counting all remaining
       symmetric values without explicit computation
    
    Time Complexity: O(max_n²) in the worst case, but often better due to early termination
    Space Complexity: O(1) - uses constant additional space

    Args:
        max_n (int): The maximum value of n to compute binomial coefficients for.
            For the original problem, this is 100.
        threshold (int): The value threshold that determines which coefficients
            are counted. For the original problem, this is 10^6 (one million).

    Returns:
        int: The count of binomial coefficients greater than the threshold.
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
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
