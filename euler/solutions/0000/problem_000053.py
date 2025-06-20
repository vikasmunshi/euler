# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 53
# https://projecteuler.net/problem=53
# Answer: 4075
# Notes:
from math import factorial
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={}, answer=4075, ), ]


def solution() -> int:
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

    Returns:
        int: The count of combinations C(n,r) that exceed one million

    Solution Approach:
    - We start from n=23 since that's the first value where combinations exceed 1 million
    - For each n, we only need to check up to the midpoint due to symmetry: C(n,r) = C(n,n-r)
    - We start with r=4 since C(100,5) is the first value of r exceeding 1 million,
      so all C(n,4) will be less than 1 million for all n <= 100
    - For odd n, the midpoint value is counted once, for even n, all values are counted twice
    """
    return sum(1 if (r == mid_point and n_is_odd) else 2
               for n in range(23, 101)
               if (n_is_odd := n % 2 != 0, mid_point := n // 2)
               for r in range(4, mid_point + 1)
               if (factorial(n) // (factorial(r) * factorial(n - r))) > 10 ** 6)


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
