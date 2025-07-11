#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 47: Distinct primes factors

Problem Statement:
The first two consecutive numbers to have two distinct prime factors are:
14 = 2 × 7
15 = 3 × 5

The first three consecutive numbers to have three distinct prime factors are:
644 = 2² × 7 × 23
645 = 3 × 5 × 43
646 = 2 × 17 × 19

Find the first four consecutive integers to have four distinct prime factors each.
What is the first of these numbers?

Solution Approach:
This solution uses a straightforward approach to find sequences of consecutive integers
with specific prime factorization properties:

1. Define a helper function that counts the number of distinct prime factors for any number
2. Iterate through integers starting from 2
3. For each number, check if it and the next n-1 consecutive integers all have
   exactly n distinct prime factors
4. Return the first number that satisfies this condition

We use efficient iteration with itertools.count and a generator expression to
minimize memory usage while testing large sequences of numbers.

Test Cases:
- For n=2: First sequence is [14, 15] (verified in problem statement)
- For n=3: First sequence is [644, 645, 646] (verified in problem statement)
- For n=4: First sequence is [134043, 134044, 134045, 134046] (our answer)

URL: https://projecteuler.net/problem=47
Answer: 134043
"""
from itertools import count

from euler.primes import prime_factor_count
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 2},  # First 2 consecutive integers with 2 distinct prime factors
        answer=14,  # 14=2×7 and 15=3×5
    ),
    ProblemArgs(
        kwargs={'n': 3},  # First 3 consecutive integers with 3 distinct prime factors
        answer=644,  # 644=2²×7×23, 645=3×5×43, 646=2×17×19
    ),
    ProblemArgs(
        kwargs={'n': 4},  # First 4 consecutive integers with 4 distinct prime factors
        answer=134043,  # The answer to the main problem
    ),
]


def solution(n: int) -> int:
    """
    Find the first of n consecutive integers, each with exactly n distinct prime factors.

    This solution searches for sequences of consecutive integers with specific prime 
    factorization properties. It efficiently iterates through integers and checks if
    each number in a consecutive sequence has exactly the required number of distinct
    prime factors.

    Args:
        n: The parameter defining both the length of the consecutive sequence and
           the number of distinct prime factors required for each integer

    Returns:
        The first integer in the sequence of n consecutive integers with the required property

    Examples:
        >>> solution(2)  # First sequence with 2 factors each
        14              # 14=2×7 and 15=3×5
        >>> solution(3)  # First sequence with 3 factors each
        644             # 644=2²×7×23, 645=3×5×43, 646=2×17×19
        >>> solution(4)  # First sequence with 4 factors each
        134043          # The answer to the main problem
    """
    return next(number for number in count(2) if not any(prime_factor_count(number + i) != n for i in range(0, n)))


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
