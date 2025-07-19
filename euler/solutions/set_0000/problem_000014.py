# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 14: Longest Collatz Sequence

Problem Statement:
The following iterative sequence is defined for the set of positive integers:

n → n/2 (n is even)
n → 3n + 1 (n is odd)

Using the rule above and starting with 13, we generate the following sequence:
13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1

It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms.
Although it has not been proved yet (Collatz Problem), it is thought that all starting
numbers finish at 1.

Which starting number, under one million, produces the longest chain?

NOTE: Once the chain starts the terms are allowed to go above one million.

Solution Approach:
This solution employs dynamic programming with memoization to efficiently calculate Collatz sequence lengths:

1. Recursive Definition: The length of a Collatz sequence starting at n is:
   - 1 if n = 1 (base case)
   - 1 + length of sequence starting at n/2 if n is even
   - 1 + length of sequence starting at 3n+1 if n is odd

2. Memoization: We use Python's @lru_cache decorator to avoid recalculating sequence
   lengths for numbers we've already processed, which dramatically improves performance.

3. Brute Force with Optimization: We check all starting numbers from 1 to max_number,
   leveraging our memoized recursive function to efficiently compute sequence lengths.

4. Result Selection: We track both the number and its sequence length, returning the
   number that produces the longest sequence.

The time complexity without memoization would be O(N·L) where N is max_number and L is
the average sequence length. With memoization, this improves significantly as many
subsequences are shared between different starting points.

Test Case:
- For max_number=1,000,000: The starting number that produces the longest chain is 837799

URL: https://projecteuler.net/problem=14
Answer: 837799
"""

from functools import lru_cache

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=14)
problem_number: int = 14

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_number': 1000000}, answer=837799, ),
]


@lru_cache(maxsize=None)
def collatz_sequence_length(number: int) -> int:
    """Calculate the length of the Collatz sequence starting from the given number.

    Uses memoization via lru_cache for performance optimization.

    Args:
        number: The starting positive integer

    Returns:
        The length of the Collatz sequence
    """
    return 1 if number == 1 else 1 + collatz_sequence_length(number // 2 if number % 2 == 0 else (3 * number) + 1)


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def start_longest_collatz_sequence(*, max_number: int) -> int:
    """Find the starting number under max_number that produces the longest Collatz sequence.

    This function systematically checks all numbers from 1 to max_number, calculating
    the length of the Collatz sequence for each using an optimized memoized approach.
    It then returns the number that generates the longest sequence.

    Args:
        max_number: The upper limit (inclusive) for starting numbers to check

    Returns:
        The starting number under or equal to max_number that produces the longest Collatz sequence

    Algorithm:
        1. For each number from 1 to max_number:
           - Calculate its Collatz sequence length using the memoized recursive function
           - Keep track of the number with the longest sequence
        2. Return the number with the maximum sequence length

    Implementation Note:
        The solution uses a functional approach with a generator expression and max() function
        to find the number with the longest sequence in a concise, efficient manner.

    Performance Considerations:
        - Time complexity: O(N) where N is max_number, though the actual runtime is much
          better due to memoization of sequence lengths
        - Space complexity: O(N) for storing memoized sequence lengths

    Example:
        >>> start_longest_collatz_sequence(max_number=10000)
        6171  # The number under 10,000 with the longest Collatz sequence
    """
    return max(((x, collatz_sequence_length(x)) for x in range(1, max_number + 1)), key=lambda i: i[1])[0]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
