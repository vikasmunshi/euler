#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 20 - Factorial digit sum
# https://projecteuler.net/problem=20
# Answer: answers={10: 27, 100: 648}
# Notes: Uses Python's built-in factorial function and arbitrary precision integers
import textwrap
from math import factorial
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},
        answer=27,
    ),
    ProblemArgs(
        kwargs={'n': 100},
        answer=648,
    ),
]


def factorial_digit_sum(n: int) -> int:
    """Calculate the sum of digits in the factorial of a number.

    This function leverages Python's built-in factorial function from the math module,
    which can handle large integers. The resulting number is converted to a string
    to easily access and sum its individual digits.

    Args:
        n: A positive integer whose factorial's digits will be summed

    Returns:
        The sum of all digits in n!
    """
    return sum(int(d) for d in str(factorial(n)))


# Cast the factorial_digit_sum function to SolutionProtocol to comply with the expected interface
# This allows us to use the function directly as our solution without additional wrapping
solution = cast(SolutionProtocol, factorial_digit_sum)

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 20: Factorial digit sum
https://projecteuler.net/problem=20

Problem Description:
n! means n × (n−1) × ... × 3 × 2 × 1.

For example, 10! = 10 × 9 × ... × 3 × 2 × 1 = 3,628,800,
and the sum of the digits in the number 10! is 3 + 6 + 2 + 8 + 8 + 0 + 0 = 27.

Find the sum of the digits in the number 100!.

Solution Approach:
- Calculate the factorial of the given number using Python's built-in factorial function
- Python's arbitrary precision integers automatically handle the large number without overflow
- Convert the resulting factorial to a string to easily access individual digits
- Sum all digits by converting each character back to an integer
- The approach is simple and efficient, avoiding the need for custom factorial implementation


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
