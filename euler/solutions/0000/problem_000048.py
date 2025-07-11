#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 48: Self powers

Problem Statement:
The series, 1¹ + 2² + 3³ + ... + 10¹⁰ = 10,405,071,317.

Find the last ten digits of the series, 1¹ + 2² + 3³ + ... + 1000¹⁰⁰⁰.

Solution Approach:
This solution utilizes Python's built-in support for arbitrary-precision integers to:

1. Calculate each term in the series (i^i) directly
2. Sum all terms in the series from 1¹ to n^n
3. Extract only the last 10 digits by applying modulo 10¹⁰ to the final sum

While the intermediate values grow extremely large (1000¹⁰⁰⁰ has approximately 3000 digits),
Python handles these large numbers efficiently. We use a generator expression to calculate
the sum term-by-term without storing all terms in memory simultaneously.

Test Cases:
- For n=10: The sum equals 10,405,071,317, with last 10 digits 0,405,071,317
- For n=100: Last 10 digits are 9,027,641,920
- For n=1000: Last 10 digits are 9,110,846,700 (the answer)
- For n=10000: Last 10 digits are 6,237,204,500 (additional test)

URL: https://projecteuler.net/problem=48
Answer: 9110846700
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},  # Calculate the sum of self-powers from 1¹ to 10¹⁰
        answer=405071317,  # Last 10 digits of 10,405,071,317
    ),
    ProblemArgs(
        kwargs={'n': 100},  # Calculate the sum of self-powers from 1¹ to 100¹⁰⁰
        answer=9027641920,  # Last 10 digits of the result
    ),
    ProblemArgs(
        kwargs={'n': 1000},  # The main problem: sum from 1¹ to 1000¹⁰⁰⁰
        answer=9110846700,  # Last 10 digits of the result
    ),
    ProblemArgs(
        kwargs={'n': 10000},  # Extended test case for even larger series
        answer=6237204500,  # Last 10 digits of the result
    ),
]


def solution(*, n: int) -> int:
    """
    Calculate the last ten digits of the sum of self-powers series.

    This function computes the sum of the series 1¹ + 2² + 3³ + ... + n^n and returns
    only the last ten digits by applying modulo 10¹⁰ to the result.

    Args:
        n: The upper limit of the series (inclusive)

    Returns:
        The last ten digits of the sum

    Examples:
        >>> solution(n=10)
        405071317  # Last 10 digits of 10,405,071,317
        >>> solution(n=100)
        9027641920
        >>> solution(n=1000)
        9110846700  # The answer to the main problem
    """
    return sum(i ** i for i in range(1, n + 1)) % 10000000000


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
