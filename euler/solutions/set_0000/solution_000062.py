#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 62: cubic_permutations

Problem Statement:
  The cube, 41063625 (345^3), can be permuted to produce two other cubes: 56623104
  (384^3) and 66430125 (405^3). In fact, 41063625 is the smallest cube which has
  exactly three permutations of its digits which are also cube. Find the smallest
  cube for which exactly five permutations of its digits are cube.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=62
Answer: None
"""
from __future__ import annotations

from collections import defaultdict
from math import ceil
from typing import Dict, Set, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase


def n_digit_cubes(digit_length_n: int) -> Tuple[int, ...]:
    """Generate all cube numbers with exactly the specified number of digits.

    This function calculates the range of integers whose cubes have exactly digit_length_n digits,
    and returns a tuple of all such cubes.

    Args:
        digit_length_n: The target number of digits for the cube numbers

    Returns:
        A tuple containing all cube numbers with exactly digit_length_n digits

    Implementation Notes:
        - Uses mathematical calculations to determine the exact range of numbers to cube
        - The start_range is calculated as the cube root of the smallest number with the specified digits
        - The stop_range is calculated as the cube root of the largest number with the specified digits
        - Both ranges are adjusted with ceil() to ensure correct boundaries
    """
    start_range: int = ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = ceil(((10 ** digit_length_n) - 1) ** (1 / 3)) + 1
    return tuple(i ** 3 for i in range(start_range, stop_range))


test_cases: list[TestCase] = [
    TestCase(
        answer=125,
        is_main_case=False,
        kwargs={'num_permutations': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=41063625,
        is_main_case=False,
        kwargs={'num_permutations': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1006012008,
        is_main_case=False,
        kwargs={'num_permutations': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=127035954683,
        is_main_case=False,
        kwargs={'num_permutations': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1000600120008,
        is_main_case=False,
        kwargs={'num_permutations': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=10569784298536,
        is_main_case=False,
        kwargs={'num_permutations': 7},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=10314675896832,
        is_main_case=False,
        kwargs={'num_permutations': 8},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=13465983902671,
        is_main_case=False,
        kwargs={'num_permutations': 9},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #62
@register_solution(problem_number=62, test_cases=test_cases)
def cubic_permutations(*, num_permutations: int) -> int:
    """Find the smallest cube for which exactly num_permutations permutations of its digits are also cube.

    This function systematically searches through cubes of increasing digit length until it finds
    a cube that has exactly the requested number of permutations that are also cubes. It returns
    the smallest such cube.

    Args:
        num_permutations: The target number of digit permutations that must also be cubes

    Returns:
        The smallest cube that has exactly num_permutations permutations of its digits
        that are also cubes

    Algorithm:
        1. Start with 2-digit cubes
        2. For each digit length:
           a. Generate all cubes with that digit length
           b. Group cubes by their digit signature (sorted digits)
           c. Find groups with exactly num_permutations members
           d. Return the smallest cube from such groups
        3. If no match is found, increase the digit length and repeat

    Implementation Notes:
        - Uses defaultdict to efficiently group cubes by their digit signature
        - Sorted digits serve as a unique identifier for permutation groups
        - The minimum value is returned to ensure we get the smallest cube in the group
        - Includes optional visualization when VISUALIZE environment variable is set

    Examples:
        >>> cubic_permutations(num_permutations=3)
        41063625  # 345³, with permutations 384³ and 405³
        >>> cubic_permutations(num_permutations=5)
        127035954683  # The original problem answer
    """
    digit_length: int = 2
    while True:
        cube_numbers: Tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: Dict[str, list[int]] = defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes[''.join(sorted(str(cube_number)))].append(cube_number)
        solutions: Set[int] = set(min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations)
        if solutions:
            if show_solution():
                print(f'Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}')
                print(f'{solutions=}')
            return min(solutions)
        digit_length += 1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(62))
