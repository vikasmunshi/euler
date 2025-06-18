#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 24: Lexicographic permutations
# https://projecteuler.net/problem=24
# Answer: 2783915460
# Notes: This solution efficiently computes the millionth lexicographic permutation
#        using a recursive approach based on factorial number system.
import textwrap
from math import factorial

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'digits': '012', 'permutation_number': 4},
        answer='120',
    ),
    ProblemArgs(
        kwargs={'digits': '012', 'permutation_number': 6},
        answer='210',
    ),
    ProblemArgs(
        kwargs={'digits': '0123456789', 'permutation_number': 10 ** 6},
        answer='2783915460',
    ),
]


def solution(*, digits: str, permutation_number: int) -> str:
    """
    Find the specific permutation of a given set of digits.

    This function recursively determines the nth lexicographic permutation of a given string of digits.
    It uses the properties of the factorial number system to efficiently find the permutation without
    generating all possible permutations.

    Args:
        digits: A string containing the characters to permute, e.g., '0123456789'
        permutation_number: The specific permutation to find (1-indexed), e.g., 1,000,000

    Returns:
        The requested permutation as a string

    Example:
        >>> solution(digits='012', permutation_number=6)
        '210'
    """
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, factorial(len(digits) - 1))
    return digits[current] + solution(digits=digits[:current] + digits[current + 1:], permutation_number=remaining + 1)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 24: Lexicographic permutations
https://projecteuler.net/problem=24

Problem Description:
A permutation is an ordered arrangement of objects.
For example, 3124 is one possible permutation of the digits 1, 2, 3 and 4.
If all of the permutations are listed numerically or alphabetically, we call it lexicographic order.
The lexicographic permutations of 0, 1 and 2 are:
012 021 102 120 201 210

Problem Statement:
What is the millionth lexicographic permutation of the digits 0, 1, 2, 3, 4, 5, 6, 7, 8 and 9?

Solution Overview:
This solution uses a mathematical approach based on the factorial number system to directly
compute the millionth permutation without generating all permutations. The algorithm:

1. For each position, determine which digit should be placed there based on the factorial number system
2. Remove the selected digit from the available set and continue recursively
3. This approach has O(n²) complexity where n is the number of digits, much better than
   generating all n! permutations

For the millionth permutation of 10 digits, the answer is 2783915460.

''').strip()

if __name__ == '__main__':
    # When this module is run directly (not imported), evaluate the solution
    # Import necessary utilities for testing and evaluation
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments for controlling execution parameters
    args = parser.parse_args()
    # Configure logging based on provided command-line arguments
    logger.setLevel(args.log_level)
    # Extract execution parameters
    timeout, max_workers = args.timeout, args.max_workers

    # Evaluate the solution with the predefined test cases
    # For this problem, we're finding the millionth lexicographic permutation of '0123456789'
    # The expected answer is '2783915460'
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
