#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 23: Non-abundant sums
# https://projecteuler.net/problem=23
# Answer: 4179871
# Notes: This solution finds the sum of all positive integers that cannot be expressed as the sum of two abundant numbers.
#        An efficient implementation using set operations and generator expressions.
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},
        answer=4179871,
    ),
]


def sum_proper_divisors(n: int) -> int:
    """Calculate the sum of all proper divisors of a number.

    A proper divisor is any positive integer that divides n evenly, excluding n itself.
    This function uses an efficient algorithm that only checks divisors up to the square root.

    Args:
        n: A positive integer

    Returns:
        The sum of all proper divisors of n
    """
    n_sqrt = int(n ** 0.5)
    return 1 + sum(i + n // i for i in range(2, n_sqrt + 1) if n % i == 0) - (n_sqrt if n_sqrt ** 2 == n else 0)


def solution() -> int:
    """Solve Project Euler problem 23: Non-abundant sums.

    Finds the sum of all positive integers that cannot be expressed as the sum of two abundant numbers.
    This is done by:
    1. Identifying all abundant numbers below 28,123 (the upper limit)
    2. Generating all possible sums of two abundant numbers
    3. Using set difference to identify numbers that cannot be expressed as such sums
    4. Summing these numbers to get the final answer

    Returns:
        The sum of all positive integers which cannot be written as the sum of two abundant numbers
    """
    abundant_numbers = [i for i in range(12, 28123 - 12) if sum_proper_divisors(i) > i]
    abundant_sums = (a + b for a in abundant_numbers for b in abundant_numbers)
    return sum(set(range(1, 28123 + 1)) - set(abundant_sums))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 23: Non-abundant sums
https://projecteuler.net/problem=23

Problem Description:
A perfect number is a number for which the sum of its proper divisors is exactly equal to the number.
For example, the sum of the proper divisors of 28 would be 1 + 2 + 4 + 7 + 14 = 28,
which means that 28 is a perfect number.

A number n is called deficient if the sum of its proper divisors is less than n
and it is called abundant if this sum exceeds n.

As 12 is the smallest abundant number, 1 + 2 + 3 + 4 + 6 = 16,
the smallest number that can be written as the sum of two abundant numbers is 24.
By mathematical analysis, it can be shown that all integers greater than 28123 can be written
as the sum of two abundant numbers. However, this upper limit cannot be reduced any further by analysis
even though it is known that the greatest number that cannot be expressed as the sum of two
abundant numbers is less than this limit.

Problem Statement:
Find the sum of all the positive integers which cannot be written as the sum of two abundant numbers.

Solution Overview:
The solution works by first identifying all abundant numbers below the limit of 28123.
Then it generates all possible sums of two abundant numbers and finds which numbers
cannot be expressed as such sums using set operations. Finally, it returns the sum
of these numbers as the answer.

''').strip()

if __name__ == '__main__':
    # When this module is run directly (not imported), evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments for controlling execution
    args = parser.parse_args()

    # Set the logging level based on command-line arguments (e.g., debug, info, warning)
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    # - timeout: maximum time allowed for solution execution
    # - max_workers: controls parallel execution of test cases
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers (4,179,871)
    # The solution is verified against the predefined test cases in problem_args_list
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
