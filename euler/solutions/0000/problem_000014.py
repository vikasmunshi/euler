#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 14 - Longest Collatz sequence
# https://projecteuler.net/problem=14
# Answer: answers={1000000: 837799}
# Notes: Uses lru_cache for memoization to optimize performance
import textwrap
from functools import lru_cache

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_number': 1000000},
        answer=837799,
    ),
]


@lru_cache(maxsize=None)
def collatz_sequence_length(number: int) -> int:
    """Calculate the length of the Collatz sequence starting from the given number.

    Uses memoization via lru_cache for performance optimization.

    Args:
        number: The starting positive integer

    Returns:
        The length of the Collatz sequence
    """
    return 1 if number == 1 else 1 + collatz_sequence_length(number // 2 if number % 2 == 0 else (3 * number) + 1)


def solution(*, max_number: int) -> int:
    """Find the starting number under max_number that produces the longest Collatz sequence.

    The function calculates the Collatz sequence length for each number from 1 to max_number,
    then returns the number that produces the longest sequence.

    Args:
        max_number: The upper limit (exclusive) for starting numbers to check

    Returns:
        The starting number under max_number that produces the longest Collatz sequence
    """
    return max(((x, collatz_sequence_length(x)) for x in range(1, max_number + 1)), key=lambda i: i[1])[0]


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 14: Longest Collatz sequence
https://projecteuler.net/problem=14

Problem Description:
The following iterative sequence is defined for the set of positive integers:

n -> n/2 (n is even)
n -> 3n + 1 (n is odd)

Using the rule above and starting with 13, we generate the following sequence:
13 -> 40 -> 20 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1.

It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms.
Although it has not been proved yet (Collatz Problem), it is thought that all starting numbers finish at 1.

Which starting number, under one million, produces the longest chain?
NOTE: Once the chain starts the terms are allowed to go above one million.

Solution Approach:
- Use recursive function with memoization to efficiently calculate sequence lengths
- Iterate through all numbers from 1 to the specified maximum
- Find the number that produces the longest Collatz sequence
- Time complexity is optimized through caching previous results

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
