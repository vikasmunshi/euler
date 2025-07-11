# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 3: Largest Prime Factor

Problem Statement:
The prime factors of 13195 are 5, 7, 13 and 29.
What is the largest prime factor of the number 600851475143?

Solution Approach:
This implementation uses an optimized trial division algorithm to find prime factors efficiently:

1. Handle the smallest prime factor (2) separately for optimization
2. For remaining odd factors, only check up to the square root of the current number
3. When a factor is found, completely divide it out before moving to the next potential factor
4. Continuously update the search limit as the number gets reduced
5. The final remaining number, if greater than 1, is the largest prime factor

The approach is efficient because:
- We only check factors up to sqrt(n), significantly reducing the search space
- We only consider odd numbers as potential factors after handling 2
- We completely remove each factor before checking the next one

Test Cases:
- For number=13195, the largest prime factor is 29
- For number=600851475143, the largest prime factor is 6857

URL: https://projecteuler.net/problem=3
Answer: 6857
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'number': 13195}, answer=29,),
    ProblemArgs(kwargs={'number': 600851475143}, answer=6857,),
]


def reduce(num: int, divisor: int) -> int:
    """Reduce a number by dividing it by a divisor until it's no longer divisible.

    Args:
        num: The number to reduce
        divisor: The divisor to use for reduction

    Returns:
        The reduced number after removing all instances of the divisor

    Example:
        >>> reduce(48, 2) # 48 / 2^4 = 3
        3
        >>> reduce(45, 3) # 45 / 3^2 = 5
        5
    """
    # First division to ensure the num is at least divisible once by divisor
    num //= divisor

    # Continue dividing as long as possible
    while num % divisor == 0:
        num //= divisor

    return num


def solution(*, number: int) -> int:
    """Find the largest prime factor of a given number.

    This function uses a trial division algorithm to find prime factors.
    It handles even numbers separately for optimization, then checks only odd
    numbers. The search space is limited to the square root of the current number.

    Args:
        number: The number to find the largest prime factor of

    Returns:
        The largest prime factor of the input number

    Example:
        >>> solution(number=13195)
        29
        >>> solution(number=600851475143)
        6857
    """
    # Handle the smallest prime factor (2) separately for optimization
    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1

    # Initialize the potential factor and the search limit
    current_factor = 3
    search_limit = int(remaining_number ** 0.5)

    # Check odd factors up to the square root of the current number
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            # When a factor is found, reduce the number and update the largest factor
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            # Update the search limit based on the new reduced number
            search_limit = int(remaining_number ** 0.5)
        current_factor += 2  # Check only odd numbers

    # If remaining_number > 1, it is the largest prime factor
    # Otherwise, return the largest factor found so far
    return remaining_number if remaining_number > 1 else largest_factor


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
