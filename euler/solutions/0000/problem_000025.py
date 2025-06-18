#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 25: 1000-digit Fibonacci number
# https://projecteuler.net/problem=25
# Answer: 4782
# Notes: This solution finds the index of the first Fibonacci number with a specified number of digits
#        using an iterative approach rather than recursion for better performance.
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 3},
        answer=12,
    ),
    ProblemArgs(
        kwargs={'n': 1000},
        answer=4782,
    ),
]


def solution(*, n: int) -> int:
    """
    Find the index of the first Fibonacci number with n digits.

    This function iteratively generates Fibonacci numbers until finding the first one
    that has at least n digits. It uses an efficient approach that only stores the
    two most recent Fibonacci numbers in memory, rather than the entire sequence.

    Args:
        n: The number of digits to look for in a Fibonacci number

    Returns:
        The index (1-based) of the first Fibonacci number with n digits

    Example:
        >>> solution(n=3)
        12 # F_12 = 144 is the first Fibonacci number with 3 digits
    """
    a, b = 1, 1
    i = 2
    while b < 10 ** (n - 1):
        a, b = b, a + b
        i += 1
    return i


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 25: 1000-digit Fibonacci number
https://projecteuler.net/problem=25

Problem Description:
The Fibonacci sequence is defined by the recurrence relation:
F_n = F_{n - 1} + F_{n - 2}, where F_1 = 1 and F_2 = 1.

Hence the first 12 terms will be:
F_1 -> 1
F_2 -> 1
F_3 -> 2
F_4 -> 3
F_5 -> 5
F_6 -> 8
F_7 -> 13
F_8 -> 21
F_9 -> 34
F_{10} -> 55
F_{11} -> 89
F_{12} -> 144

The 12th term, F_{12}, is the first term to contain three digits.

Problem Statement:
What is the index of the first term in the Fibonacci sequence to contain 1000 digits?

Solution Overview:
This solution uses an iterative approach to generate Fibonacci numbers one by one
until finding the first one with the required number of digits. We efficiently track
only the two most recent numbers in the sequence at any time, keeping memory usage
constant regardless of how many Fibonacci numbers need to be calculated.

For the case of 1000 digits, the answer is 4782, meaning F_4782 is the first
Fibonacci number with 1000 digits.

''').strip()

if __name__ == '__main__':
    # When this module is run directly (not imported), evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments for controlling execution parameters
    args = parser.parse_args()

    # Set the logging level based on command-line arguments (e.g., debug, info, warning)
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    # - timeout: maximum time allowed for solution execution
    # - max_workers: controls parallel execution of test cases
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
