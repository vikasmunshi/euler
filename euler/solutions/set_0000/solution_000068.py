#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 68: magic_5_gon_ring

Problem Statement:
  Consider the following "magic" 3-gon ring, filled with the numbers 1 to 6, and
  each line adding to nine.   Working clockwise, and starting from the group of
  three with the numerically lowest external node (4,3,2 in this example), each
  solution can be described uniquely. For example, the above solution can be
  described by the set: 4,3,2; 6,2,1; 5,1,3. It is possible to complete the ring
  with four different totals: 9, 10, 11, and 12. There are eight solutions in
  total.  TotalSolution Set 94,2,3; 5,3,1; 6,1,2 94,3,2; 6,2,1; 5,1,3 102,3,5;
  4,5,1; 6,1,3 102,5,3; 6,3,1; 4,1,5 111,4,6; 3,6,2; 5,2,4 111,6,4; 5,4,2; 3,2,6
  121,5,6; 2,6,4; 3,4,5 121,6,5; 3,5,4; 2,4,6  By concatenating each group it is
  possible to form 9-digit strings; the maximum string for a 3-gon ring is
  432621513. Using the numbers 1 to 10, and depending on arrangements, it is
  possible to form 16- and 17-digit strings. What is the maximum 16-digit string
  for a "magic" 5-gon ring?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=68
Answer: None
"""
from __future__ import annotations

from collections import namedtuple
from itertools import permutations
from typing import List, Set, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase

Line = namedtuple('Line', ['outer', 'inner_1', 'inner_2'])
Ring = namedtuple('Ring', ['outer', 'inner'])

test_cases: list[TestCase] = [
    TestCase(
        answer=432621513,
        is_main_case=False,
        kwargs={'result_length': 9, 'ring_size': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=462723831516,
        is_main_case=False,
        kwargs={'result_length': 12, 'ring_size': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=6531031914842725,
        is_main_case=False,
        kwargs={'result_length': 16, 'ring_size': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=692122310348451151719,
        is_main_case=False,
        kwargs={'result_length': 21, 'ring_size': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=87494612611315115314321027,
        is_main_case=False,
        kwargs={'result_length': 26, 'ring_size': 7},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=5981381151614621624114712731039,
        is_main_case=False,
        kwargs={'result_length': 31, 'ring_size': 8},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=109518511716166215271473133812841149,
        is_main_case=False,
        kwargs={'result_length': 36, 'ring_size': 9},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #68
@register_solution(problem_number=68, test_cases=test_cases)
def magic_5_gon_ring(*, result_length: int, ring_size: int) -> int:
    """Find the maximum magic number for n-gon ring using tuple-based approach.

    This function implements an efficient algorithm to find the maximum "magic number"
    for an n-gon ring, based on the mathematical insights described in the module docstring.
    The key optimizations include:

    1. Focusing on inner node permutations rather than full permutations of all 2n numbers
    2. Early rejection of invalid configurations based on inner node adjacent sums
    3. Deterministic calculation of outer nodes based on the required line sum
    4. Canonical form enforcement (starting with the smallest outer node)

    For a 5-gon ring with numbers 1-10, this reduces the search space by several orders
    of magnitude compared to a brute force approach.

    Args:
        ring_size: Size of the n-gon ring (number of outer nodes)
        result_length: Maximum length of the result as a string when concatenating the digits of each line

    Returns:
        The maximum magic number that fits within the result_length constraint
    """
    # Initialize variables for the ring size and result constraints
    n: int = ring_size
    index_range_n: Tuple[int, ...] = tuple(range(1, n))
    max_magic_number: int = 0  # Track the maximum valid magic number found
    max_ring, max_lines = None, None  # Store the best configuration for visualization
    inner_loop_count: int = 0  # Counter to track the number of loops processed
    outer_loop_count: int = 0  # Counter to track the number of loops processed

    # Generate all possible arrangements of inner nodes
    # Limit numbers to 1-9 if possible to ensure correct digit count in result
    for inner_choice in permutations(range(1, min(9, 2 * n) + 1), n):
        outer_loop_count += 1
        # Calculate the sums of adjacent inner nodes (each pair appears in one line)
        inner_sums: Tuple[int, ...] = tuple(inner_choice[i] + inner_choice[(i + 1) % n] for i in range(n))

        # Mathematical insight: If there are duplicate inner sums, we can't have a valid magic ring
        # This efficiently filters out many invalid configurations early
        if len(set(inner_sums)) != n:
            continue

        # Determine available candidates for outer nodes (numbers not used for inner nodes)
        outer_candidates: Set[int] = set(n for n in range(1, (2 * n) + 1) if n not in inner_choice)

        # Start with the smallest outer node (canonical form requirement)
        outer_choice: List[int] = [min(outer_candidates)]
        outer_candidates.remove(outer_choice[0])

        # Calculate the required line sum based on the first line
        line_sum: int = outer_choice[0] + inner_sums[0]

        # Deterministically calculate the remaining outer nodes
        # For each position i, the required outer node value is: line_sum - inner_sums[i]
        for i in index_range_n:
            inner_loop_count += 1
            try:
                # Use the walrus operator to calculate and remove the required value in one step
                outer_candidates.remove(required := line_sum - inner_sums[i])
            except KeyError:
                # If the required number is not available, this configuration is invalid
                break
            else:
                # Add the required outer node to our configuration
                outer_choice.append(required)
        else:
            # This block executes if the for loop completes without breaking
            # Construct the lines of the ring, each containing (outer, inner_1, inner_2)
            lines = tuple(zip(outer_choice, inner_choice, inner_choice[1:] + inner_choice[:1]))

            # Convert the ring configuration to a concatenated string of digits
            magic_number: int = int(''.join(''.join(str(num) for num in line) for line in lines))

            # Update the maximum if this is a larger magic number
            if max_magic_number < magic_number:
                max_magic_number = magic_number
                max_ring = Ring(outer=tuple(outer_choice), inner=tuple(inner_choice))
                max_lines = tuple(Line(*line) for line in lines)
    if show_solution():
        print(f'Ring Size: {ring_size}; Inner Loop Count: {inner_loop_count}; Outer Loop Count: {outer_loop_count}; '
              f'Magic Number: {max_magic_number}; Ring: {max_ring}; Lines: {max_lines}')
    assert result_length == len(str(max_magic_number)), 'Result length does not match expected value'
    return max_magic_number


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(68))
