#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 24: lexicographic_permutations

Problem Statement:
  A permutation is an ordered arrangement of objects. For example, 3124 is one
  possible permutation of the digits 1, 2, 3 and 4. If all of the permutations are
  listed numerically or alphabetically, we call it lexicographic order. The
  lexicographic permutations of 0, 1 and 2 are: 012   021   102   120   201   210
  What is the millionth lexicographic permutation of the digits 0, 1, 2, 3, 4, 5,
  6, 7, 8 and 9?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=24
Answer: None
"""
from __future__ import annotations

from math import factorial

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer='120',
        is_main_case=False,
        kwargs={'digits': '012', 'permutation_number': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer='210',
        is_main_case=False,
        kwargs={'digits': '012', 'permutation_number': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer='2783915460',
        is_main_case=False,
        kwargs={'digits': '0123456789', 'permutation_number': 1000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #24
@register_solution(problem_number=24, test_cases=test_cases)
def lexicographic_permutations(*, digits: str, permutation_number: int) -> str:
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
        >>> lexicographic_permutations(digits='012', permutation_number=4)
        '120'
        >>> lexicographic_permutations(digits='0123456789', permutation_number=1000000)
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
                   lexicographic_permutations(digits=digits[:current] + digits[current + 1:],
                                              permutation_number=remaining + 1))
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(24))
