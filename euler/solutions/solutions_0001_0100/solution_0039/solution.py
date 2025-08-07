#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 39: Integer Right Triangles.

  Problem Statement:
    If p is the perimeter of a right angle triangle with integral length
    sides, {a, b, c}, there are exactly three solutions for p = 120.

    {20, 48, 52}, {24, 45, 51}, {30, 40, 50}

    For which value of p <= 1000, is the number of solutions maximised?

  Solution Approach:
    To solve this problem, iterate over all possible integral perimeters p up
    to 1000. For each p, find all sets of integer sides (a, b, c) such that
    a + b + c = p and they satisfy the Pythagorean theorem a^2 + b^2 = c^2.
    Efficiently check candidate triples by limiting the range of a and b
    based on p. Keep a count of valid solutions for each perimeter. Finally,
    return the perimeter with the maximum number of solutions. Consider using
    optimized loops and mathematical properties of right triangles to reduce
    computation time.

  Test Cases:
    preliminary:
      max_perimeter=100,
      answer=60.

    main:
      max_perimeter=1000,
      answer=840.

    extended:
      max_perimeter=10000,
      answer=5040.

      max_perimeter=100000,
      answer=55440.

      max_perimeter=1000000,
      answer=720720.


  Answer: 840
  URL: https://projecteuler.net/problem=39
"""
from __future__ import annotations

from collections import Counter
from math import gcd

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=39, test_case_category=TestCaseCategory.EXTENDED)
def integer_right_triangles(*, max_perimeter: int) -> int:
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter ** 0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append((perimeter := (2 * m * (m + n))))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=39, time_out_in_seconds=300, mode='evaluate'))
