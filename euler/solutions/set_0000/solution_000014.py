#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 14: longest_collatz_sequence

Problem Statement:
  The following iterative sequence is defined for the set of positive integers:  n
  \to n/2 (n is even) n \to 3n + 1 (n is odd) Using the rule above and starting
  with 13, we generate the following sequence: 13 \to 40 \to 20 \to 10 \to 5 \to
  16 \to 8 \to 4 \to 2 \to 1. It can be seen that this sequence (starting at 13
  and finishing at 1) contains 10 terms. Although it has not been proved yet
  (Collatz Problem), it is thought that all starting numbers finish at 1. Which
  starting number, under one million, produces the longest chain? NOTE: Once the
  chain starts the terms are allowed to go above one million.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=14
Answer: None
"""
from __future__ import annotations

from functools import lru_cache

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=837799,
        is_main_case=False,
        kwargs={'max_number': 1000000},
        solution_execution_time=None,
        solved=False
    ),
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


# Register this function as a solution for problem #14
@register_solution(problem_number=14, test_cases=test_cases)
def longest_collatz_sequence(*, max_number: int) -> int:
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
        >>> longest_collatz_sequence(max_number=10000)
        6171  # The number under 10,000 with the longest Collatz sequence
    """
    return max(((x, collatz_sequence_length(x)) for x in range(1, max_number + 1)), key=lambda i: i[1])[0]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(14))
