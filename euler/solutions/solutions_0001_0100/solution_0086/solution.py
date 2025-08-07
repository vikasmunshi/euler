#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 86: Cuboid Route.

  Problem Statement:
    A spider, S, sits in one corner of a cuboid room, measuring 6 by 5 by 3, and
    a fly, F, sits in the opposite corner. By travelling on the surfaces of
    the room the shortest "straight line" distance from S to F is 10 and the
    path is shown on the diagram.

    However, there are up to three "shortest" path candidates for any given
    cuboid and the shortest route doesn't always have integer length.

    It can be shown that there are exactly 2060 distinct cuboids, ignoring
    rotations, with integer dimensions, up to a maximum size of M by M by M,
    for which the shortest route has integer length when M = 100. This is the
    least value of M for which the number of solutions first exceeds two
    thousand; the number of solutions when M = 99 is 1975.

    Find the least value of M such that the number of solutions first exceeds
    one million.

  Solution Approach:
    To solve this problem, consider the shortest path a spider can take on
    the surfaces of an M x M x M cuboid from one corner to the opposite corner.
    This shortest path corresponds to the shortest distance between two points
    on the net (unfolded surfaces) of the cuboid.

    The key insight is that the shortest path on the surface is the minimum of
    the distance across three possible rectangular unfoldings combining two
    dimensions at a time.

    Focus on the relationship between the dimensions and the possible integer
    shortest paths. Use a mathematical approach to count how many cuboids with
    integer dimensions up to M have an integer shortest path. This involves
    iterating over possible dimensions and checking the hypotenuse values.

    Efficient implementation and careful handling of counting distinct
    cuboids (ignoring rotations) are essential. Use properties of right
    triangles and the Pythagorean theorem to determine when paths are integer-
    valued.

    Incrementally increase M until the count of solutions exceeds one million.

  Test Cases:
    preliminary:
      target_solutions=1975,
      answer=99.

      target_solutions=2000,
      answer=100.

    main:
      target_solutions=1000000,
      answer=1818.


  Answer: 1818
  URL: https://projecteuler.net/problem=86
"""
from __future__ import annotations

from itertools import count
from math import sqrt

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=86, test_case_category=TestCaseCategory.EXTENDED)
def cuboid_route(*, target_solutions: int) -> int:
    result: int = 0
    for a in count(1):
        for b_plus_c in range(1, 2 * a + 1):
            if sqrt(a ** 2 + b_plus_c ** 2).is_integer():
                result += b_plus_c // 2 if b_plus_c <= a + 1 else (2 * a - b_plus_c + 2) // 2
                if result >= target_solutions:
                    return a
    return -1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=86, time_out_in_seconds=300, mode='evaluate'))
