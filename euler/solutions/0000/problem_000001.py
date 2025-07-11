#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 1: Multiples of 3 and 5

Problem Statement:
If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9.
The sum of these multiples is 23.
Find the sum of all the multiples of 3 or 5 below 1000.

Solution Approach:
This implementation uses a mathematical optimization based on the arithmetic sum formula
rather than iterating through each number. By applying the inclusion-exclusion principle,
we avoid double-counting numbers that are multiples of both 3 and 5.

The formula used is:
Sum = Sum of multiples of 3 + Sum of multiples of 5 - Sum of multiples of 15

For each term, we use the arithmetic series sum formula: n(n+1)/2 * d,
where n is the count of terms and d is the common difference (3, 5, or 15).

Test Cases:
- For max_limit=10, the answer is 23
- For max_limit=1000, the answer is 233,168

URL: https://projecteuler.net/problem=1
Answer: 233,168
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_limit': 10}, answer=23, ),
    ProblemArgs(kwargs={'max_limit': 1000}, answer=233168, ),
]


def solution(*, max_limit: int) -> int:
    """
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
