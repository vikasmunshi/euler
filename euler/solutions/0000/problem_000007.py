#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 7
https://projecteuler.net/problem=7

Problem Statement:
By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13.
What is the 10001st prime number?

Approach:
This solution implements a modified Sieve of Eratosthenes to find prime numbers. Instead of marking
composite numbers directly, we work with indices that map to odd numbers and only handle the odd
numbers (since all even numbers except 2 are composite). We use the property that odd numbers can
be represented as 2n+1, where n is the index in our number list.

The upper bound for the search space is estimated using the Prime Number Theorem,
which states that the nth prime number is approximately n*log(n).

Known answers:
- 6th prime number: 13
- 10001st prime number: 104743
"""
import textwrap
from math import log

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Define test cases with expected answers for validation
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 6},  # Find the 6th prime number
        answer=13,  # The 6th prime number is 13
    ),
    ProblemArgs(
        kwargs={'n': 10001},  # Find the 10001st prime number
        answer=104743,  # The 10001st prime number is 104743
    ),
]


def solution(*, n: int) -> int:
    """
    Find the nth prime number.

    This implementation uses a modified Sieve of Eratosthenes optimized for finding
    the nth prime number. It specifically focuses on odd numbers, since all even numbers
    except 2 are composite.

    Args:
        n: The position of the prime number to find (e.g., n=6 finds the 6th prime)

    Returns:
        The nth prime number

    Note:
        - For n=1, we return 2 (the first prime number) as a special case
        - For n>1, we search through odd numbers using the sieve method
        - The formula i+j+(2*i*j) generates indices of composite numbers
    """
    # Handle special case: the first prime number is 2
    if n == 1:
        return 2

    # Estimate the upper bound for the nth prime using Prime Number Theorem
    max_expected_value = int(n * log(n))

    # Initialize the sieve array where index i corresponds to number 2i+1
    numbers = list(range(0, max_expected_value + 1))

    # Apply the sieve algorithm to mark composite numbers
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not prime as 0
            except IndexError:
                break

    # Extract all non-zero values (representing prime indices)
    # Convert back to actual prime numbers using the formula 2i+1
    # Select the (n-2)th element (accounting for the fact that we've excluded 2,
    # and our indexing starts at 0)
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

# Preserve the original docstring for the solution function
solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 7
https://projecteuler.net/problem=7
By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13.
What is the 10001st prime number?


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
