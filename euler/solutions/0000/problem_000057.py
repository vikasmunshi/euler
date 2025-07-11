#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 57: Square Root Convergents

Problem Statement:
It is possible to show that the square root of two can be expressed as an infinite continued fraction.
√2 = 1 + 1/(2 + 1/(2 + 1/(2 + ...)))

By expanding this for the first four iterations, we get:
1 + 1/2 = 3/2 = 1.5
1 + 1/(2 + 1/2) = 7/5 = 1.4
1 + 1/(2 + 1/(2 + 1/2)) = 17/12 = 1.41666...
1 + 1/(2 + 1/(2 + 1/(2 + 1/2))) = 41/29 = 1.41379...

The next three expansions are 99/70, 239/169, and 577/408, but the eighth expansion, 
1393/985, is the first example where the number of digits in the numerator exceeds 
the number of digits in the denominator.

In the first one-thousand expansions, how many fractions contain a numerator with more 
digits than the denominator?

Solution Approach:
This solution uses a recurrence relation to efficiently compute the convergents of the 
continued fraction expansion of √2. For each expansion, we check if the numerator has 
more digits than the denominator and count those instances.

The recurrence relation used is:
- h_n = h_{n-1} + 2*k_{n-1}
- k_n = h_{n-1} + k_{n-1}

where h_n is the numerator and k_n is the denominator of the nth convergent.

Test Cases:
- For expansions=10: 1 fraction has more digits in numerator than denominator
- For expansions=100: 15 fractions have more digits in numerator than denominator
- For expansions=1000: 153 fractions have more digits in numerator than denominator
- For expansions=10000: 1508 fractions have more digits in numerator than denominator

URL: https://projecteuler.net/problem=57
Answer: 153
"""
from sys import set_int_max_str_digits

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'expansions': 10 ** 1}, answer=1, ),  # 10 expansions
    ProblemArgs(kwargs={'expansions': 10 ** 2}, answer=15, ),  # 100 expansions
    ProblemArgs(kwargs={'expansions': 10 ** 3}, answer=153, ),  # 1,000 expansions (the problem's target)
    ProblemArgs(kwargs={'expansions': 10 ** 4}, answer=1508, ),  # 10,000 expansions
    # ProblemArgs(kwargs={'expansions': 10 ** 5}, answer=15052, ), # 100,000 expansions
]


def solution(*, expansions: int) -> int:
    """
    Count the fractions in the continued fraction expansion of √2 where the numerator 
    has more digits than the denominator.

    This solution efficiently computes the convergents of the continued fraction expansion
    of √2 using a recurrence relation. For each expansion, we check if the numerator has
    more digits than the denominator and count those instances.

    Args:
        expansions: The number of expansions to compute

    Returns:
        The count of fractions where the numerator has more digits than the denominator

    Example:
        >>> solution(expansions=1000)
        153
    """
    # Initialize variables for the recurrence relation
    # Starting with h_0=1, k_0=1 (representing 1/1)
    numerator, denominator, result = 1, 1, 0

    # Compute each expansion using the recurrence relation
    for _ in range(expansions):
        # Calculate the next convergent using the recurrence relation:
        # h_n = h_{n-1} + 2*k_{n-1}
        # k_n = h_{n-1} + k_{n-1}
        numerator, denominator = numerator + 2 * denominator, numerator + denominator

        # Check if the numerator has more digits than the denominator
        # Using boolean as integer (True = 1, False = 0) to increment result
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            # Handle potential integer string conversion limit in Python
            # This occurs with very large numbers
            set_int_max_str_digits(0)  # Disable the limit
            print(f'sys.set_int_max_str_digits(0) {expansions=}, {len(str(numerator))=}, {len(str(denominator))=}')
            result += len(str(numerator)) > len(str(denominator))

    # Return the total count of fractions meeting the criteria
    return result


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
