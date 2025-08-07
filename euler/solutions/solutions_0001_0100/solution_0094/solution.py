#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 94: Almost Equilateral Triangles.

  Problem Statement:
    It is easily proved that no equilateral triangle exists with integral
    length sides and integral area. However, the almost equilateral triangle
    5-5-6 has an area of 12 square units.

    We shall define an almost equilateral triangle to be a triangle for which
    two sides are equal and the third differs by no more than one unit.

    Find the sum of the perimeters of all almost equilateral triangles with
    integral side lengths and area and whose perimeters do not exceed one
    billion (1 000 000 000).

  Solution Approach:
    To solve this problem, one can leverage the properties of almost equilateral
    triangles and the relationship between their side lengths and area.
    Using the formula for the area of a triangle with two equal sides, we can
    derive equations involving integer side lengths and areas.

    A key insight is to reduce the problem to solving specific Pell equations,
    which arise naturally from the constraints on sides and area.
    Generating solutions to these Pell equations systematically allows us to
    find all qualifying triangles with integral area and side lengths that satisfy
    the perimeter limit. Efficient iteration and checking of these solutions
    will yield the desired sum of perimeters.

  Test Cases:
    main:
      max_perimeter=1000000000,
      answer=518408346.


  Answer: 518408346
  URL: https://projecteuler.net/problem=94
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=94, test_case_category=TestCaseCategory.EXTENDED)
def almost_equilateral_triangles(*, max_perimeter: int) -> int:
    s, s1, s2, m, p = (0, 1, 1, 1, 0)
    while p <= max_perimeter:
        s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
        p = 3 * s2 - m
    return s


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=94, time_out_in_seconds=300, mode='evaluate'))
