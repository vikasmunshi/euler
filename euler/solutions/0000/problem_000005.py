#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 5
# https://projecteuler.net/problem=5
# Answer: 232792560
# Notes: Calculates the least common multiple (LCM) of all integers from 1 to n
import textwrap
from functools import reduce  # For performing cumulative operations
from math import gcd  # Greatest common divisor function

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# List of test cases with expected answers
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},  # First test case with n=10
        answer=2520,  # Expected answer for n=10
    ),
    ProblemArgs(
        kwargs={'n': 20},  # Second test case with n=20
        answer=232792560,  # Expected answer for n=20
    ),
]


def solution(*, n: int) -> int:
    """Calculate the smallest positive number divisible by all integers from 1 to n.

    This function computes the least common multiple (LCM) of all integers from 1 to n.
    It uses the mathematical property that LCM(a,b) = (a*b)/gcd(a,b) and extends it
    to multiple numbers using the reduce function.

    Args:
        n (int): The upper limit of the range of integers to consider.
            Must be a positive integer.

    Returns:
        int: The smallest positive number that is evenly divisible by all
            integers from 1 to n.

    Time Complexity: O(n log n) - iterating through n numbers with gcd calculation
    Space Complexity: O(1) - uses constant extra space regardless of input size
    """
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

# Preserve the original problem description as required
solution.__doc__ = textwrap.dedent('''
solution to Project Euler problem 5
https://projecteuler.net/problem=5
2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.
What is the smallest positive number that is evenly divisible with no remainder by all of the numbers from 1 to 20?


''').strip()

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
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
