#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 94:

Problem Statement:
It is easily proved that no equilateral triangle exists with integral length sides and integral area. However, the
almost equilateral triangle 5-5-6 has an area of 12 square units.

We shall define an almost equilateral triangle to be a triangle for which two sides are equal and the third differs by
no more than one unit.

Find the sum of the perimeters of all almost equilateral triangles with integral side lengths and area and whose
perimeters do not exceed one billion (1\,000\,000\,000).

Solution Approach:
This problem involves finding special triangles with two equal sides and the third side differing by at most 1 unit.
Additionally, these triangles must have integral side lengths and area.

For a triangle with sides (a, a, a±1), we can use the formula for the area of a triangle given its sides:
Area = √(s(s-a)(s-b)(s-c)) where s = (a+b+c)/2 (semi-perimeter)

For our almost equilateral triangles, this would be:
- For (a, a, a+1): Area = √((3a+1)/2 · (a+1)/2 · (a+1)/2 · (a-1)/2)
- For (a, a, a-1): Area = √((3a-1)/2 · (a-1)/2 · (a-1)/2 · (a+1)/2)

For the area to be an integer, the expression under the square root must be a perfect square.

The solution uses a recurrence relation derived from Pell's equation to efficiently generate
all valid triangles without having to check each possible side length individually.

The implementation uses the following variables:
- s0, s1: consecutive terms in the recurrence relation
- s: running sum of perimeters (the answer)
- p: perimeter of the current triangle
- m: alternates between 1 and -1 to generate triangles with sides (a,a,a+1) and (a,a,a-1)

Test Cases:
The sum of perimeters of all almost equilateral triangles with integral side lengths and area
and perimeters not exceeding 10^9 is 518408346.

URL: https://projecteuler.net/problem=94
Answer: 518408346
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=94)
problem_number: int = 94

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={'max_perimeter': 10 ** 9}, answer=518408346, ),
                                      ]


# Register this function as a solution for problem #94 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_almost_equilateral_triangle_perimeters(*, max_perimeter: int) -> int:
    """
    Calculate the sum of perimeters of all almost equilateral triangles with
    integral side lengths and area, whose perimeters do not exceed max_perimeter.

    An almost equilateral triangle has two equal sides and the third differs by
    at most one unit.

    Args:
        max_perimeter: The maximum perimeter to consider (1,000,000,000 for the problem)

    Returns:
        The sum of all valid triangle perimeters

    Implementation notes:
        - s: Running sum of perimeters (the answer)
        - s1, s2: Terms in the recurrence relation for generating valid side lengths
        - m: Alternates between 1 and -1 to generate triangles with sides (a,a,a+1) and (a,a,a-1)
        - p: Current triangle perimeter
    """
    s, s1, s2, m, p = 0, 1, 1, 1, 0
    while p <= max_perimeter:
        s, s1, s2, m = s + p, s2, (4 * s2 - s1 + 2 * m), -m
        p = 3 * s2 - m
    return s


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
