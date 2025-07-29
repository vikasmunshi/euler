#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 86: cuboid_route

Problem Statement:
  A spider, S, sits in one corner of a cuboid room, measuring 6 by 5 by 3, and a
  fly, F, sits in the opposite corner. By travelling on the surfaces of the room
  the shortest "straight line" distance from S to F is 10 and the path is shown on
  the diagram.   However, there are up to three "shortest" path candidates for any
  given cuboid and the shortest route doesn't always have integer length. It can
  be shown that there are exactly 2060 distinct cuboids, ignoring rotations, with
  integer dimensions, up to a maximum size of M by M by M, for which the shortest
  route has integer length when M = 100. This is the least value of M for which
  the number of solutions first exceeds two thousand; the number of solutions when
  M = 99 is 1975. Find the least value of M such that the number of solutions
  first exceeds one million.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=86
Answer: None
"""
from __future__ import annotations

from itertools import count
from math import sqrt

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=99,
        is_main_case=False,
        kwargs={'target_solutions': 1975},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=100,
        is_main_case=False,
        kwargs={'target_solutions': 2000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1818,
        is_main_case=False,
        kwargs={'target_solutions': 1000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #86
@register_solution(problem_number=86, test_cases=test_cases)
def cuboid_route(*, target_solutions: int) -> int:
    """Find the smallest M where the number of cuboids with integer shortest paths exceeds target_solutions.

    Args:
        target_solutions: The threshold number of solutions to exceed

    Returns:
        The smallest M such that the number of distinct cuboids with integer shortest paths exceeds target_solutions
    """
    result: int = 0  # Counter for valid cuboids found so far

    # Iterate through possible values of 'a' (we consider cuboids with a ≥ b ≥ c > 0)
    for a in count(1):
        # Iterate through all possible values of b+c
        for b_plus_c in range(1, 2 * a + 1):
            # Check if the shortest path length is an integer
            # The formula √(a² + (b+c)²) gives the shortest path when unfolding the cuboid
            if sqrt(a ** 2 + b_plus_c ** 2).is_integer():
                # Count valid cuboids with dimensions (a,b,c) where b+c = b_plus_c
                # For b+c ≤ a+1: count is ⌊(b+c)/2⌋
                # For b+c > a+1: count is ⌊(2a-b+c+2)/2⌋
                # This accounts for the constraint a ≥ b ≥ c > 0
                result += (b_plus_c // 2 if b_plus_c <= a + 1 else (2 * a - b_plus_c + 2) // 2)

                # If we've found enough solutions, return the current M value
                if result >= target_solutions:
                    return a

    return -1  # This should never be reached for valid inputs


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(86))
