#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 91: Right Triangles With Integer Coordinates.

  Problem Statement:
    The points P(x_1, y_1) and Q(x_2, y_2) are plotted at integer coordinates
    and are joined to the origin, O(0,0), to form \u0394OPQ.

    There are exactly fourteen triangles containing a right angle that can be
    formed when each coordinate lies between 0 and 2 inclusive; that is,
    0 \u2264 x_1, y_1, x_2, y_2 \u2264 2.

    Given that 0 \u2264 x_1, y_1, x_2, y_2 \u2264 50, how many right triangles can
    be formed?

  Solution Approach:
    To solve this problem, consider all possible points with integer
    coordinates between 0 and the given limit (50 in this case). For each
    pair of points P and Q, check if the triangle formed with the origin is a
    right triangle. Use the property that a triangle is right angled if the
    dot product of the vectors representing two sides is zero.

    More specifically, compute vectors OP, OQ, and PQ, and check the
    perpendicularity conditions for the three angles. Optimizing the search
    by leveraging symmetry and avoiding duplicate triangles can improve
    efficiency. Counting all valid configurations gives the number of
    right triangles.

  Test Cases:
    preliminary:
      max_num=2,
      answer=14.

    main:
      max_num=50,
      answer=14234.


  Answer: 14234
  URL: https://projecteuler.net/problem=91
"""
from __future__ import annotations

from math import gcd

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=91, test_case_category=TestCaseCategory.EXTENDED)
def right_triangles_with_integer_coordinates(*, max_num: int) -> int:
    triangles_at_p_or_q = sum(
            (min(x * m // y, m * (max_num - y) // x) for x in range(1, max_num + 1) for y in range(1, max_num) for m in
             [gcd(x, y)]))
    triangles_at_p_or_q *= 2
    triangles_at_origin = 3 * max_num ** 2
    return triangles_at_p_or_q + triangles_at_origin


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=91, time_out_in_seconds=300, mode='evaluate'))
