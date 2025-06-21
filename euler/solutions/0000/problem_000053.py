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

    In general, binom{n}{r} = n! // (r! * (nor)!), where:
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
    The computation leverages symmetry in binomial coefficients to optimize
    calculation and minimize redundant work.

    Args:
        max_n (int): The maximum value of n to compute binomial coefficients for.
        threshold (int): The value threshold that determines which coefficients
            are counted.

    Returns:
        int: The count of binomial coefficients greater than the threshold.
    """
    count = 0
    for n in range(1, max_n + 1):
        c = 1  # C(n, 0) is always 1
        for r in range(0, n // 2 + 1):  # Only compute up to n//2 due to symmetry
            if c > threshold:
                count += (n - 2 * r + 1)  # Count all symmetric combinations directly and exit the loop
                break
            else:
                c = c * (n - r) // (r + 1)  # Compute the next binomial coefficient dynamically from the current one
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
