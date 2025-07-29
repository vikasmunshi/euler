#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 94: almost_equilateral_triangles

Problem Statement:
  It is easily proved that no equilateral triangle exists with integral length
  sides and integral area. However, the almost equilateral triangle 5-5-6 has an
  area of 12 square units. We shall define an almost equilateral triangle to be a
  triangle for which two sides are equal and the third differs by no more than one
  unit. Find the sum of the perimeters of all almost equilateral triangles with
  integral side lengths and area and whose perimeters do not exceed one billion
  (1\,000\,000\,000).

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=94
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=518408346,
        is_main_case=False,
        kwargs={'max_perimeter': 1000000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #94
@register_solution(problem_number=94, test_cases=test_cases)
def almost_equilateral_triangles(*, max_perimeter: int) -> int:
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
    raise SystemExit(evaluate_solutions(94))
