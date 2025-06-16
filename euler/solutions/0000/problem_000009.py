#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 9
# https://projecteuler.net/problem=9
# Answer: answers={12: 60, 1000: 31875000}
# Notes: 

"""
Pythagorean Triplet Problem (Project Euler #9)

This module solves Project Euler problem 9, which asks for the product of the
Pythagorean triplet (a, b, c) that satisfies a + b + c = 1000.

A Pythagorean triplet is a set of three natural numbers where a < b < c and
a² + b² = c². The solution finds the unique triplet with a specified sum and
returns the product a*b*c.

Example:
    For sum = 12, the triplet is (3, 4, 5) and the product is 60.
    For sum = 1000, the product is 31,875,000.

Tests:
    Two test cases are included: sum_sides=12 and sum_sides=1000.
"""

import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Define test cases for validation
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'sum_sides': 12},  # First test case: sum = 12 (3,4,5)
        answer=60,                 # Expected answer: 3*4*5 = 60
    ),
    ProblemArgs(
        kwargs={'sum_sides': 1000}, # Second test case: sum = 1000
        answer=31875000,            # Expected answer
    ),
]


def solution(*, sum_sides: int) -> int | None:
    """
    Find the product of the Pythagorean triplet (a,b,c) with sum equal to sum_sides.

    A Pythagorean triplet is a set of three natural numbers (a < b < c) such that
    a² + b² = c². This function finds a triplet where a + b + c = sum_sides and
    returns their product (a*b*c).

    Args:
        sum_sides: The required sum of the three sides (a + b + c)

    Returns:
        int: The product a*b*c of the Pythagorean triplet
        None: If no Pythagorean triplet exists with the given sum

    Algorithm:
        1. Iterate through possible values of 'a' (optimized range)
        2. For each 'a', iterate through possible values of 'b' (optimized range)
        3. Calculate 'c' as sum_sides - a - b
        4. Check if a² + b² = c² (Pythagorean condition)
        5. Return the product a*b*c for the first triplet found

    Optimization notes:
        - 'a' must be less than sum_sides/4 due to constraints
        - 'b' must be at least 'a' and less than sum_sides/2
        - Using generator expression with next() for efficiency
    """
    try:
        return next(a * b * c
                    for a in range(1, sum_sides // 4 + 1)  # Optimized range for 'a'
                    for b in range(a, sum_sides // 2)      # Optimized range for 'b'
                    for c in (sum_sides - a - b,)          # Calculate 'c' directly
                    if a ** 2 + b ** 2 == c ** 2)          # Pythagorean condition
    except StopIteration:
        pass  # Return None if no triplet is found


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

# Preserve the original docstring as specified in the requirements
# This maintains compatibility with the Project Euler problem format
solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 9
https://projecteuler.net/problem=9
A Pythagorean triplet is a set of three natural numbers, a \lt b \lt c, for which,
a^2 + b^2 = c^2.
For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.
There exists exactly one Pythagorean triplet for which a + b + c = 1000.
Find the product abc.


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
