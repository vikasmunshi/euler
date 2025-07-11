# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 5: Smallest Multiple

Problem Statement:
2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.
What is the smallest positive number that is evenly divisible by all of the numbers from 1 to 20?

Solution Approach:
This problem asks for the least common multiple (LCM) of all integers from 1 to n.

The implementation uses the following mathematical concepts and optimizations:

1. The LCM of two numbers a and b can be calculated using the formula: LCM(a,b) = (a*b)/GCD(a,b)
   where GCD is the greatest common divisor

2. Python's math.gcd function efficiently computes the greatest common divisor using 
   the Euclidean algorithm

3. The functools.reduce function elegantly extends the LCM calculation to multiple numbers by
   applying the LCM operation cumulatively across the range

4. Since the LCM of 1 and any number is that number itself, we start the range from 2
   and use 1 as the initial value for reduce

The solution has O(n log n) time complexity, which is efficient even for large values of n.

Test Cases:
- For n=10: 2520
- For n=20: 232792560

URL: https://projecteuler.net/problem=5
Answer: 232792560
"""
from functools import reduce
from math import gcd

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10}, answer=2520, ),  # First test case with n=10 Expected answer for n=10
    ProblemArgs(kwargs={'n': 20}, answer=232792560, ),  # Second test case with n=20 Expected answer for n=20
]


def solution(*, n: int) -> int:
    """Calculate the smallest positive number divisible by all integers from 1 to n.

    This function computes the least common multiple (LCM) of all integers from 1 to n.
    It uses the mathematical property that LCM(a,b) = (a*b)/gcd(a,b) and extends it
    to multiple numbers using the reduce function.

    Args:
        n (int): The upper limit of the range of integers to consider.
            Must be a positive integer.

    Returns:
        int: The smallest positive number that is evenly divisible by all
            integers from 1 to n.

    Time Complexity: O(n log n) - iterating through n numbers with gcd calculation
    Space Complexity: O(1) - uses constant extra space regardless of input size
    """
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


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
