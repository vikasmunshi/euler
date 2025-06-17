#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 16 - Power digit sum
# https://projecteuler.net/problem=16
# Answer: answers={15: 26, 1000: 1366}
# Notes: Leverages Python's built-in arbitrary precision arithmetic
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'power': 15},
        answer=26,
    ),
    ProblemArgs(
        kwargs={'power': 1000},
        answer=1366,
    ),
]


def solution(*, power: int, base: int = 2) -> int:
    """Calculate the sum of digits in the number base^power.

    This solution takes advantage of Python's built-in support for arbitrary-precision
    integers, which automatically handles large numbers without overflow issues.

    Args:
        power: The exponent to which the base is raised
        base: The base number to be raised to the specified power (default: 2)

    Returns:
        The sum of all individual digits in the resulting number
    """
    return sum(int(i) for i in str(base ** power))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 16: Power digit sum
https://projecteuler.net/problem=16

Problem Description:
2^{15} = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.

What is the sum of the digits of the number 2^{1000}?

Solution Approach:
- Calculate the exact value of 2^1000 using arbitrary precision arithmetic
- Convert the resulting number to a string to easily access individual digits
- Sum all digits by converting each character back to an integer
- Python handles large integers automatically, making this calculation straightforward
- The approach generalizes to any base and power combination

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
