#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script provides a solution to Project Euler problem 6:
https://projecteuler.net/problem=6

The problem statement:
The sum of the squares of the first ten natural numbers is:
1^2 + 2^2 + ... + 10^2 = 385.

The square of the sum of the first ten natural numbers is:
(1 + 2 + ... + 10)^2 = 55^2 = 3025.

Hence, the difference between the sum of the squares of the first ten natural numbers and the square of the sum is:
3025-385 = 2640.

The goal is to find the difference between the sum of the squares of the first `n` natural numbers and the square of the sum for a given `n`.

Answer:
    answers={10: 2640, 100: 25164150}
"""

import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# List of problem arguments and their corresponding answers for validation purposes
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},  # Test case where n=10
        answer=2640,  # Expected answer for n=10
    ),
    ProblemArgs(
        kwargs={'n': 100},  # Test case where n=100
        answer=25164150,  # Expected answer for n=100
    ),
]


def solution(*, n: int) -> int:
    """
    Computes the difference between the square of the sum of the first `n`
    natural numbers and the sum of the squares of the first `n` natural numbers.

    Args:
        n (int): The number up to which the calculations are performed.

    Returns:
        int: The difference between the square of the sum and the sum of the squares.

    Explanation:
    - The sum of the first `n` natural numbers is calculated as:
      S = (n * (n + 1) // 2)
    - The square of the sum is:
      S^2
    - The sum of the squares of the first `n` natural numbers is calculated as:
      Sum of squares = (2 * n + 1) * (n + 1) * n // 6
    - Finally, the difference is:
      S^2 - Sum of squares
    """
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 6
https://projecteuler.net/problem=6
The sum of the squares of the first ten natural numbers is,
1^2 + 2^2 + ... + 10^2 = 385.
The square of the sum of the first ten natural numbers is,
(1 + 2 + ... + 10)^2 = 55^2 = 3025.
Hence the difference between the sum of the squares of the first ten natural numbers and the square of the sum is 3025 - 385 = 2640.
Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
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
