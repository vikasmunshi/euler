#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 34: Digit factorials

Problem Statement:
145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145.

Find the sum of all numbers which are equal to the sum of the factorial of their digits.

Note: As 1! = 1 and 2! = 2 are not sums they are not included.

Solution Approach:
This solution systematically searches for numbers that equal the sum of their digit factorials.
The approach is optimized based on mathematical reasoning to limit the search space:

1. An upper bound is established by recognizing that for any d-digit number where d ≥ 8:
   - The largest possible sum of digit factorials would be d×9! = d×362,880
   - This sum cannot exceed 8×9! = 2,903,040 for an 8-digit number
   - But the smallest 8-digit number is 10,000,000, which exceeds this maximum sum
   - Therefore, we only need to check numbers up to 7 digits

2. The implementation uses combinations_with_replacement to efficiently generate all
   possible digit combinations, avoiding redundant calculations when the same digit appears
   multiple times.

3. For each combination of digits, the algorithm:
   - Calculates the sum of their factorials
   - Verifies that this sum has the expected number of digits
   - Confirms that all the original digits appear in the sum (possibly in a different order)
   - Double-checks that the sum indeed equals the sum of factorials of its own digits

This approach significantly reduces the search space from millions of numbers to a much
smaller set of possible combinations.

URL: https://projecteuler.net/problem=34
Answer: 40730
"""
from itertools import combinations_with_replacement

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=40730, ),
]


def solution() -> int:
    """Find the sum of all numbers equal to the sum of the factorials of their digits.

    This function identifies all numbers where the sum of the factorials of each digit
    equals the number itself. It excludes 1 and 2 as specified in the problem statement.

    Returns:
        The sum of all numbers that equal the sum of the factorials of their digits

    Example:
        >>> solution()
        40730  # Includes numbers like 145 (1! + 4! + 5! = 145)
    """
    upper_bound_num_digits = 7 + 1
    factorial = {'0': 1, '1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5040, '8': 40320, '9': 362880}
    return sum(
        int(num)
        for num_digits in range(2, upper_bound_num_digits)
        for digits in combinations_with_replacement('0123456789', num_digits)
        for num in (str(sum(factorial[d] for d in digits)),)
        if len(num) == num_digits
        and all(digit in num for digit in digits)
        and num == str(sum(factorial[n] for n in num))
    )


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
