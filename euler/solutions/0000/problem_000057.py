# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 57
# https://projecteuler.net/problem=57
# Answer: 153
# Notes: This solution calculates continued fraction expansions of sqrt(2) and counts
# how many of these expansions have a numerator with more digits than the denominator.
# The recurrence relation for the convergents is used to efficiently compute each expansion.
# For large numbers of expansions, set_int_max_str_digits(0) is used to handle potential
# integer size limitations.
from sys import set_int_max_str_digits
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases for the solution with expected answers
# Each case specifies the number of expansions to calculate and the expected count of
# fractions where the numerator has more digits than the denominator
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'expansions': 10 ** 1}, answer=1, ),  # 10 expansions
    ProblemArgs(kwargs={'expansions': 10 ** 2}, answer=15, ), # 100 expansions
    ProblemArgs(kwargs={'expansions': 10 ** 3}, answer=153, ), # 1,000 expansions (the problem's target)
    ProblemArgs(kwargs={'expansions': 10 ** 4}, answer=1508, ), # 10,000 expansions
    # ProblemArgs(kwargs={'expansions': 10 ** 5}, answer=15052, ), # 100,000 expansions
]


def solution(*, expansions: int) -> int:
    r"""
    Solution to Project Euler problem 57: Square root convergents
    https://projecteuler.net/problem=57

    It is possible to show that the square root of two can be expressed as an infinite continued fraction.
    \sqrt 2 =1+ \frac 1 {2+ \frac 1 {2 +\frac 1 {2+ ...}}}

    By expanding this for the first four iterations, we get:
    1 + \frac 1 2 = \frac  32 = 1.5
    1 + \frac 1 {2 + \frac 1 2} = \frac 7 5 = 1.4
    1 + \frac 1 {2 + \frac 1 {2+\frac 1 2}} = \frac {17}{12} = 1.41666 ...
    1 + \frac 1 {2 + \frac 1 {2+\frac 1 {2+\frac 1 2}}} = \frac {41}{29} = 1.41379 ...

    The next three expansions are \frac {99}{70}, \frac {239}{169}, and \frac {577}{408}, but the eighth expansion,
    \frac {1393}{985}, is the first example where the number of digits in the numerator exceeds the number of digits
    in the denominator.

    In the first one-thousand expansions, how many fractions contain a numerator with more digits than the denominator?

    Args:
        expansions (int): The number of expansions to compute

    Returns:
        int: The count of fractions where the numerator has more digits than the denominator

    Notes:
        The solution uses the recurrence relation for continued fraction convergents:
        h_n = h_{n-1} + 2*k_{n-1}
        k_n = h_{n-1} + k_{n-1}

        where h_n is the numerator and k_n is the denominator of the nth convergent.
        For extremely large values of expansions, Python's string conversion limit might be exceeded,
        which is handled by disabling the limit with set_int_max_str_digits(0).
    """
    # Initialize variables for the recurrence relation
    # Starting with h_0=1, k_0=1 (representing 1/1)
    numerator, denominator, result = 1, 1, 0

    # Compute each expansion using the recurrence relation
    for _ in range(expansions):
        # Calculate the next convergent using the recurrence relation:
        # h_n = h_{n-1} + 2*k_{n-1}
        # k_n = h_{n-1} + k_{n-1}
        numerator, denominator = numerator + 2 * denominator, numerator + denominator

        # Check if the numerator has more digits than the denominator
        # Using boolean as integer (True = 1, False = 0) to increment result
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            # Handle potential integer string conversion limit in Python
            # This occurs with very large numbers
            set_int_max_str_digits(0)  # Disable the limit
            print(f'sys.set_int_max_str_digits(0) {expansions=}, {len(str(numerator))=}, {len(str(denominator))=}')
            result += len(str(numerator)) > len(str(denominator))

    # Return the total count of fractions meeting the criteria
    return result


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
