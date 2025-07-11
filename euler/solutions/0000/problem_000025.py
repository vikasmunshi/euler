# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 25: 1000-digit Fibonacci number

Problem Statement:
The Fibonacci sequence is defined by the recurrence relation:
F_n = F_{n-1} + F_{n-2}, where F_1 = 1 and F_2 = 1.

Hence the first 12 terms will be:
F_1 = 1
F_2 = 1
F_3 = 2
F_4 = 3
F_5 = 5
F_6 = 8
F_7 = 13
F_8 = 21
F_9 = 34
F_10 = 55
F_11 = 89
F_12 = 144

The 12th term, F_12, is the first term to contain three digits.
What is the index of the first term in the Fibonacci sequence to contain 1000 digits?

Solution Approach:
This implementation uses an iterative approach to generate Fibonacci numbers until reaching
the first number with the desired number of digits. The algorithm maintains only the two most
recent Fibonacci numbers in memory, making it memory-efficient. We determine the number of
digits by comparing each Fibonacci number with 10^(n-1), which is the smallest n-digit number.

Test Cases:
- For n=3, the answer is 12 (F_12 = 144 is the first 3-digit Fibonacci number)
- For n=1000, the answer is 4782

URL: https://projecteuler.net/problem=25
Answer: 4782
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 3}, answer=12, ),
    ProblemArgs(kwargs={'n': 1000}, answer=4782, ),
]


def solution(*, n: int) -> int:
    """
    Find the index of the first Fibonacci number with n digits.

    This solution iteratively generates Fibonacci numbers using the recurrence relation
    F_n = F_{n-1} + F_{n-2}, starting with F_1 = F_2 = 1. It continues until finding the
    first number with at least n digits, determined by checking if the number is greater
    than or equal to 10^(n-1).

    Args:
        n: The number of digits to look for in a Fibonacci number

    Returns:
        The index (1-based) of the first Fibonacci number with n digits

    Example:
        >>> solution(n=3)
        12  # F_12 = 144 is the first Fibonacci number with 3 digits
        >>> solution(n=1000)
        4782  # The answer to the original problem
    """
    a, b = 1, 1
    i = 2
    while b < 10 ** (n - 1):
        a, b = b, a + b
        i += 1
    return i


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
