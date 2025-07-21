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

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=24)
problem_number: int = 24

# Define the test cases for validating the solution
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


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def lexicographic_permutation(*, digits: str, permutation_number: int) -> str:
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
        >>> lexicographic_permutation(digits='012', permutation_number=4)
        '120'
        >>> lexicographic_permutation(digits='0123456789', permutation_number=1000000)
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
    result: str = (digits[current] +
                   lexicographic_permutation(digits=digits[:current] + digits[current + 1:],
                                             permutation_number=remaining + 1))
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
