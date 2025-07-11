# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 6: Sum Square Difference

Problem Statement:
The sum of the squares of the first ten natural numbers is,
1² + 2² + ... + 10² = 385.

The square of the sum of the first ten natural numbers is,
(1 + 2 + ... + 10)² = 55² = 3025.

Hence the difference between the sum of the squares of the first ten natural numbers 
and the square of the sum is 3025 - 385 = 2640.

Find the difference between the sum of the squares of the first one hundred natural 
numbers and the square of the sum.

Solution Approach:
This problem can be solved using mathematical formulas rather than explicit computation:

1. Sum of first n natural numbers: n(n+1)/2
   This is a well-known formula attributed to Gauss

2. Sum of squares of first n natural numbers: n(n+1)(2n+1)/6
   This is a standard mathematical formula derived from sequence analysis

3. The difference is calculated by:
   [Sum of first n natural numbers]² - [Sum of squares of first n natural numbers]
   = [n(n+1)/2]² - n(n+1)(2n+1)/6

Using these formulas allows us to compute the result in O(1) time complexity 
regardless of the input size, which is much more efficient than using loops.

Test Cases:
- For n=10: 2640
- For n=100: 25164150

URL: https://projecteuler.net/problem=6
Answer: 25164150
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10}, answer=2640, ),  # Test case where n=10 Expected answer for n=10
    ProblemArgs(kwargs={'n': 100}, answer=25164150, ),  # Test case where n=100 Expected answer for n=100
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
