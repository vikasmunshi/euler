# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 57
# https://projecteuler.net/problem=57
# Answer: 153
# Notes: This solution calculates the number of fractions in the continued fraction
# expansion of sqrt(2) where the numerator has more digits than the denominator.
# We use a recurrence relation to efficiently compute each expansion:
# numerator = numerator + 2 * denominator
# denominator = numerator + denominator (using the previous numerator value)
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases for the solution with expected answers
# Each case specifies a number of expansions to calculate and the expected result
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'expansions': 10}, answer=1, ),
    # For first 10 expansions, 1 fraction has numerator with more digits
    ProblemArgs(kwargs={'expansions': 100}, answer=15, ),
    # For first 100 expansions, 15 fractions have numerator with more digits
    ProblemArgs(kwargs={'expansions': 1000}, answer=153, ),
    # For first 1000 expansions (the problem statement), 153 fractions
    ProblemArgs(kwargs={'expansions': 10000}, answer=1508, ),  # Extended test case for 10000 expansions
]


def solution(*, expansions: int) -> int:
    r"""
    solution to Project Euler problem 57
    https://projecteuler.net/problem=57
    It is possible to show that the square root of two can be expressed as an infinite continued fraction.
    \sqrt 2 =1+ \frac 1 {2+ \frac 1 {2 +\frac 1 {2+ ...}}}
    By expanding this for the first four iterations, we get:
    1 + \frac 1 2 = \frac  32 = 1.5

    1 + \frac 1 {2 + \frac 1 2} = \frac 7 5 = 1.4

    1 + \frac 1 {2 + \frac 1 {2+\frac 1 2}} = \frac {17}{12} = 1.41666 ...

    1 + \frac 1 {2 + \frac 1 {2+\frac 1 {2+\frac 1 2}}} = \frac {41}{29} = 1.41379 ...

    The next three expansions are \frac {99}{70}, \frac {239}{169}, and \frac {577}{408},
    but the eighth expansion, \frac {1393}{985},
    is the first example where the number of digits in the numerator exceeds the number of digits in the denominator.
    In the first one-thousand expansions, how many fractions contain a numerator with more digits than the denominator?
    
    Solution Approach:
    1. Initialize variables for numerator and denominator starting at 1
    2. Use a recurrence relation to generate each expansion:
       - New numerator = previous numerator + 2 * previous denominator
       - New denominator = previous numerator + previous denominator
    3. For each expansion:
       - Calculate new fraction using the recurrence relation
       - Compare digit count of numerator and denominator
       - Increment counter if numerator has more digits
    4. Return the total count of fractions where numerator has more digits
    
    """
    # Initialize variables:
    # - numerator and denominator start at 1 for the first iteration
    # - result will count fractions with numerator having more digits than denominator
    numerator, denominator, result = 1, 1, 0

    # Generate each expansion of sqrt(2) as a continued fraction
    for _ in range(expansions):
        # Calculate the next fraction in the sequence using the recurrence relation
        # For each expansion, the new values are derived from the previous ones:
        # - New numerator = previous numerator + 2 * previous denominator
        # - New denominator = previous numerator + previous denominator
        # This efficiently generates the sequence without needing to compute the actual continued fraction
        numerator, denominator = numerator + 2 * denominator, numerator + denominator

        # Check if the numerator has more digits than the denominator
        # by converting both to strings and comparing their lengths
        if len(str(numerator)) > len(str(denominator)):
            result += 1

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
