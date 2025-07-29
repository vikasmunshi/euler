#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 52: permuted_multiples

Problem Statement:
  It can be seen that the number, 125874, and its double, 251748, contain exactly
  the same digits, but in a different order. Find the smallest positive integer,
  x, such that 2x, 3x, 4x, 5x, and 6x, contain the same digits.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=52
Answer: None
"""
from __future__ import annotations

import sys

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=125874,
        is_main_case=False,
        kwargs={'multiples': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=142857,
        is_main_case=False,
        kwargs={'multiples': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=142857,
        is_main_case=False,
        kwargs={'multiples': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=142857,
        is_main_case=False,
        kwargs={'multiples': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=142857,
        is_main_case=False,
        kwargs={'multiples': 6},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #52
@register_solution(problem_number=52, test_cases=test_cases)
def permuted_multiples(*, multiples: int) -> int:
    """
    Find the smallest positive integer whose multiples contain the same digits.

    This function searches for the smallest number x where x, 2x, 3x, ..., up to
    multiples×x all contain exactly the same digits (in any order). It works by
    converting each multiple to a string, sorting its digits, and comparing them.

    Args:
        multiples: The number of consecutive multiples to check (between 2 and 6)

    Returns:
        The smallest positive integer with the permuted multiples property

    Examples:
        >>> permuted_multiples(multiples=2)
        125874  # 125874 and 251748 contain the same digits
        >>> permuted_multiples(multiples=6)
        142857  # 142857, 285714, 428571, 571428, 714285, 857142 all contain the same digits

    Raises:
        ValueError: If multiples is not between 2 and 6, or if no solution is found
    """
    if not (isinstance(multiples, int) and 1 < multiples < 7):
        # For multiples=7 or higher, there likely does not exist a solution where a positive integer and all its first n
        # multiples contain the exact same digits.
        raise ValueError('multiples must be an integer between 2 and 6, both inclusive.')
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):  # not considering the know solution for multiples = 2
        # 1. `for multiple in multiples_range` - Iterates through each multiple (1, 2, 3, etc. up to the specified
        #     'multiples' parameter)
        # 2. `i * multiple` - Calculates each multiple of the current number i being tested
        # 3. `str(i * multiple)` - Converts each multiple to a string, so we can work with its individual digits
        # 4. `sorted(str(i * multiple))` - Sorts the digits of each multiple in ascending order
        #     - For example, if i=142857 and multiple=2, then i*multiple=285714, and sorted would yield
        #       ['1','2','4','5','7','8']
        #
        # 5. `''.join(sorted(str(i * multiple)))` - transforms sorted list (unhashable) of digits to string (hashable)
        #     - This produces a canonical representation of the digit set regardless of their original order
        #     - Example: 285714 becomes '124578'
        #
        # 6. `{...}` - Creates a set of these sorted digit strings for all multiples
        #     - A set only contains unique elements, so if all multiples have the same digits (in any order),
        #       this set will contain only one element
        #
        # 7. `len({...}) == 1` - Checks if the set has exactly one element
        #     - If true, all multiples contain exactly the same digits (just arranged differently)
        #     - If false, at least one multiple has a different set of digits
        if len({''.join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return i
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(52))
