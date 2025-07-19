#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 91:

Problem Statement:
The points P(x₁, y₁) and Q(x₂, y₂) are plotted at integer co-ordinates and are joined to the origin, O(0,0), to form
triangle OPQ.
    <see problem description at https://projecteuler.net/problem=91>
There are exactly fourteen triangles containing a right angle that can be formed when each co-ordinate lies between
0 and 2 inclusive; that is, 0 ≤ x₁, y₁, x₂, y₂ ≤ 2.

Given that 0 ≤ x₁, y₁, x₂, y₂ ≤ 50, how many right triangles can be formed?

Solution Approach:
A right triangle can have its right angle at any of the three vertices: O, P, or Q.

1. When the right angle is at O (the origin), P and Q must lie on the x and y axes, respectively.
   This gives max_num² possible triangles.

2. When the right angle is at P, the problem becomes more complex and involves calculating
   specific points based on perpendicular vectors to OP.

3. When the right angle is at Q, it's similar to case 2 by symmetry.

The solution uses vector properties and the greatest common divisor (gcd) to efficiently
count all right triangles without enumerating all possible combinations of points.

Test Cases:
- max_num=2: 14 right triangles
- max_num=50: 14234 right triangles

URL: https://projecteuler.net/problem=91
Answer: 14234
"""
from math import gcd

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=91)
problem_number: int = 91

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_num': 2}, answer=14),
    ProblemArgs(kwargs={'max_num': 50}, answer=14234),
]


# Register this function as a solution for problem #91 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def num_right_triangles_with_integer_coordinates(*, max_num: int) -> int:
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
    raise SystemExit(evaluate_solutions(problem_number))
