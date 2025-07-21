# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 68: Magic n-gon Ring

Problem Statement:
Consider the following "magic" 3-gon ring, filled with the numbers 1 to 6, and each line adding to nine.

Working clockwise, and starting from the group of three with the numerically lowest external node
(4,3,2 in this example), each solution can be described uniquely. For example, the above solution can be described
by the set: 4,3,2; 6,2,1; 5,1,3.

It is possible to complete the ring with four different totals: 9, 10, 11, and 12.  There are eight solutions in total.

Total  Solution Set
9  4,2,3; 5,3,1; 6,1,2
9  4,3,2; 6,2,1; 5,1,3
10  2,3,5; 4,5,1; 6,1,3
10  2,5,3; 6,3,1; 4,1,5
11  1,4,6; 3,6,2; 5,2,4
11  1,6,4; 5,4,2; 3,2,6
12  1,5,6; 2,6,4; 3,4,5
12  1,6,5; 3,5,4; 2,4,6

By concatenating each group it is possible to form 9-digit strings; the maximum string for a 3-gon ring is 432621513.

Using the numbers 1 to 10, and depending on arrangements, it is possible to form 16- and 17-digit strings.
What is the maximum **16-digit** string for a "magic" 5-gon ring?

Mathematical Insights:

1. Structure of an n-gon Ring:
   - An n-gon ring consists of n outer nodes and n inner nodes, forming a total of 2n nodes.
   - Each "line" in the ring contains an outer node and two consecutive inner nodes.
   - For a "magic" n-gon ring, all n lines must sum to the same value (the "magic sum").

2. Constraints and Properties:
   - For the problem at hand (using numbers 1 to 10 for a 5-gon ring):
     a) The total sum of all numbers from 1 to 10 is 55.
     b) Each inner node appears in exactly 2 lines, while each outer node appears in exactly 1 line.
     c) The sum of all line totals equals the sum of all outer nodes plus twice the sum of all inner nodes.

3. Search Space Reduction:
   - For a valid configuration, if we fix the inner nodes, the outer nodes are determined by the constraint
     that all lines must sum to the same value.
   - By starting with the smallest outer node (canonical form), we ensure uniqueness of solutions.
   - We can further reduce the search space by placing 10 in an outer position to ensure a 16-digit result.

4. Optimization Techniques:
   - Early rejection: If the inner nodes have duplicate "inner_sums" (sum of adjacent inner nodes),
     then it's impossible to have consistent line sums across the ring.
   - Deterministic outer node placement: Once we've chosen inner nodes and the smallest outer node,
     all other outer nodes are uniquely determined by the required line sum.

5. Time Complexity Analysis:
   - The naive approach would examine all permutations of 10 numbers, which is 10! ≈ 3.6 million.
   - Our optimized approach significantly reduces this by:
     a) Only permuting inner nodes (reduction to P(10,5) permutations)
     b) Early filtering based on inner sums
     c) Deterministically calculating outer nodes rather than permuting them

Solution Approach:
This solution leverages these mathematical insights through a streamlined algorithm:

1. Generate all possible arrangements of n inner nodes (from numbers 1 to 10).
2. For each arrangement:
   - Calculate the sums of adjacent inner nodes.
   - Skip arrangements with duplicate inner sums (impossible to have consistent line totals).
   - Select the smallest available number as the first outer node.
   - Calculate the required line sum based on the first line.
   - Deterministically calculate the remaining outer nodes based on the required line sum.
   - If all required outer nodes are available, construct the "magic" n-gon ring.
   - Calculate the concatenated string value and track the maximum valid result.

Test Cases:
- 3-gon ring (9-digit result): 432621513
- 4-gon ring (12-digit result): 462723831516
- 5-gon ring (16-digit result): 6531031914842725
- 6-gon ring (21-digit result): 692122310348451151719
- 7-gon ring (26-digit result): 87494612611315115314321027
- 8-gon ring (31-digit result): 5981381151614621624114712731039
- 9-gon ring (36-digit result): 109518511716166215271473133812841149

URL: https://projecteuler.net/problem=68
Answer: 6531031914842725
"""
from __future__ import annotations

from collections import namedtuple
from itertools import permutations
from typing import List, Set, Tuple

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=68)
problem_number: int = 68

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'ring_size': 3, 'result_length': 3 * 3}, answer=432621513, ),
    ProblemArgs(kwargs={'ring_size': 4, 'result_length': 4 * 3}, answer=462723831516, ),
    ProblemArgs(kwargs={'ring_size': 5, 'result_length': 5 * 3 + 1}, answer=6531031914842725, ),
    ProblemArgs(kwargs={'ring_size': 6, 'result_length': 6 * 3 + 3}, answer=692122310348451151719, ),
    ProblemArgs(kwargs={'ring_size': 7, 'result_length': 7 * 3 + 5}, answer=87494612611315115314321027, ),
    ProblemArgs(kwargs={'ring_size': 8, 'result_length': 8 * 3 + 7}, answer=5981381151614621624114712731039, ),
    ProblemArgs(kwargs={'ring_size': 9, 'result_length': 9 * 3 + 9}, answer=109518511716166215271473133812841149, ),
]
Line = namedtuple('Line', ['outer', 'inner_1', 'inner_2'])
Ring = namedtuple('Ring', ['outer', 'inner'])


# Register this function as a solution for problem #68 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def n_gong_ring_magic_number(*, ring_size: int, result_length: int) -> int:
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
    raise SystemExit(evaluate_solutions(problem_number))
