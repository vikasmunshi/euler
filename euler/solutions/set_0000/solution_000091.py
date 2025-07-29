#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 91: right_triangles_with_integer_coordinates

Problem Statement:
  The points P(x_1, y_1) and Q(x_2, y_2) are plotted at integer co-ordinates and
  are joined to the origin, O(0,0), to form \triangle OPQ.   There are exactly
  fourteen triangles containing a right angle that can be formed when each co-
  ordinate lies between 0 and 2 inclusive; that is, 0 \le x_1, y_1, x_2, y_2 \le
  2.   Given that 0 \le x_1, y_1, x_2, y_2 \le 50, how many right triangles can be
  formed?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=91
Answer: None
"""
from __future__ import annotations

from math import gcd

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=14,
        is_main_case=False,
        kwargs={'max_num': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=14234,
        is_main_case=False,
        kwargs={'max_num': 50},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #91
@register_solution(problem_number=91, test_cases=test_cases)
def right_triangles_with_integer_coordinates(*, max_num: int) -> int:
    """
    Calculate the number of right triangles with integer coordinates within the given bounds.

    For a grid of size max_num × max_num, count how many right triangles can be formed with:
    - One vertex at the origin (0,0)
    - The other two vertices P(x₁,y₁) and Q(x₂,y₂) with integer coordinates within the grid
    - A right angle at any of the three vertices

    Args:
        max_num: The maximum coordinate value (grid size is max_num × max_num)

    Returns:
        The total count of right triangles with integer coordinates
    """
    # Count triangles with right angles at P or Q (using vector properties)
    # For each primitive vector (x,y), we find how many valid integer points can form
    # a right triangle by creating perpendicular vectors
    triangles_at_p_or_q = sum(
        min(x * m // y, m * (max_num - y) // x)
        for x in range(1, max_num + 1)
        for y in range(1, max_num)
        for m in [gcd(x, y)]  # m is the GCD of x and y
    )

    # Double count for symmetry (right angle at P or right angle at Q)
    triangles_at_p_or_q *= 2

    # Add triangles with right angle at origin (O)
    # These are formed when P is on x-axis and Q is on y-axis, or vice versa
    # There are 3*max_num² such triangles (including degenerate cases)
    triangles_at_origin = 3 * max_num ** 2

    return triangles_at_p_or_q + triangles_at_origin


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(91))
