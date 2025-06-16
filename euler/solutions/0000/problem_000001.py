#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 1
# https://projecteuler.net/problem=1
# Answer: 10: 23, 1000: 233,168
# Notes: 
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_limit': 10},
        answer=23,
    ),
    ProblemArgs(
        kwargs={'max_limit': 1000},
        answer=233168,
    ),
]


def solution(*, max_limit: int) -> int:
    """
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9.
    The sum of these multiples is 23.
    Find the sum of all the multiples of 3 or 5 below 1000.

    This solution uses the arithmetic sum formula to efficiently calculate
    the sum of multiples without iterating through each number. It applies
    the inclusion-exclusion principle to avoid double-counting numbers that
    are multiples of both 3 and 5 (i.e., multiples of 15).

    Args:
        max_limit: An integer representing the upper bound (exclusive)

    Returns:
        The sum of all multiples of 3 or 5 below max_limit

    Example:
        >>> solution(max_limit=10)
        23
        >>> solution(max_limit=1000)
        233,168
    """

    def sum_multiples(number: int) -> int:
        """Calculate the sum of multiples of 'number' up-to max_limit using formula for arithmetic sum: n(n+1)/2."""
        terms = (max_limit - 1) // number
        return number * terms * (terms + 1) // 2

    # Apply inclusion-exclusion principle:
    # sum(multiples of 3) + sum(multiples of 5) - sum(multiples of 15)
    return sum_multiples(3) + sum_multiples(5) - sum_multiples(3 * 5)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

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
