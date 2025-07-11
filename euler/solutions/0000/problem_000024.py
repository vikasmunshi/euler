#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 24: Lexicographic permutations

Problem Statement:
A permutation is an ordered arrangement of objects. For example, 3124 is one possible permutation
of the digits 1, 2, 3 and 4. If all of the permutations are listed numerically or alphabetically,
we call it lexicographic order. The lexicographic permutations of 0, 1 and 2 are:
012   021   102   120   201   210
What is the millionth lexicographic permutation of the digits 0, 1, 2, 3, 4, 5, 6, 7, 8 and 9?

Solution Approach:
This implementation uses a factorial-based algorithm to efficiently compute the millionth permutation
without generating all permutations. For a string of length n, there are (n-1)! permutations starting
with each possible first character. By using integer division and modulo operations with factorials,
we can determine exactly which character should be at each position.

The algorithm works recursively:
1. Calculate which character comes first using permutation_number ÷ (n-1)!
2. Remove this character from the available digits
3. Update the permutation number for the remaining digits
4. Recursively find the permutation of the remaining digits

Test Cases:
- For digits='012' and permutation_number=4, the answer is '120'
- For digits='012' and permutation_number=6, the answer is '210'
- For digits='0123456789' and permutation_number=1,000,000, the answer is '2783915460'

URL: https://projecteuler.net/problem=24
Answer: 2783915460
"""

# The factorial function is central to this solution as the algorithm relies on the
# factorial number system to efficiently compute lexicographic permutations
from math import factorial

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    # Test case 1: Find the 4th permutation of '012'
    # All permutations: 012, 021, 102, 120, 201, 210
    # The 4th permutation is '120'
    ProblemArgs(kwargs={'digits': '012', 'permutation_number': 4}, answer='120', ),

    # Test case 2: Find the 6th (last) permutation of '012'
    # The 6th permutation is '210'
    ProblemArgs(kwargs={'digits': '012', 'permutation_number': 6}, answer='210', ),

    # Test case 3: The actual Project Euler problem - find the millionth permutation
    # of the digits 0-9. This is the main test case for the problem.
    ProblemArgs(kwargs={'digits': '0123456789', 'permutation_number': 10 ** 6}, answer='2783915460', ),
]


def solution(*, digits: str, permutation_number: int) -> str:
    """
    Find the specified lexicographic permutation of a given set of digits.

    This solution uses a factorial-based algorithm to efficiently find the nth permutation
    without generating all possible permutations. It works by recursively determining which
    character should be placed at each position based on factorial calculations.

    Args:
        digits: A string containing the characters to permute
        permutation_number: The lexicographic permutation number to find (1-indexed)

    Returns:
        The requested permutation as a string

    Example:
        >>> solution(digits='012', permutation_number=4)
        '120'
        >>> solution(digits='0123456789', permutation_number=1000000)
        '2783915460'
    """
    # Base case: If only one character remains, return it (no permutations possible)
    if len(digits) == 1:
        return digits

    # Calculate which character comes first in this permutation and what permutation number
    # remains for the rest of the string
    # 1. Convert permutation_number from 1-indexed to 0-indexed by subtracting 1
    # 2. Integer divide by (n-1)! to find the index of the first character
    # 3. Use modulo to determine the remaining permutation number (convert back to 1-indexed)
    current, remaining = divmod(permutation_number - 1, factorial(len(digits) - 1))

    # Build the permutation recursively:
    # 1. Select the character at position 'current'
    # 2. Remove this character from the digits string for the recursive call
    # 3. Recursively find the permutation of the remaining characters
    # 4. Concatenate the current character with the result of the recursive call
    return digits[current] + solution(digits=digits[:current] + digits[current + 1:], permutation_number=remaining + 1)


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
