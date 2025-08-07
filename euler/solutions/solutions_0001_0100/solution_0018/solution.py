#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 18: Maximum Path Sum I.

  Problem Statement:
    By starting at the top of the triangle below and moving to adjacent numbers on
    the row below, the maximum total from top to bottom is 23.

    3
    7 4
    2 4 6
    8 5 9 3

    That is, 3 + 7 + 4 + 9 = 23.

    Find the maximum total from top to bottom of the triangle below:

    75
    95 64
    17 47 82
    18 35 87 10
    20 04 82 47 65
    19 01 23 75 03 34
    88 02 77 73 07 63 67
    99 65 04 28 06 16 70 92
    41 41 26 56 83 40 80 70 33
    41 48 72 33 47 32 37 16 94 29
    53 71 44 65 25 43 91 52 97 51 14
    70 11 33 28 77 73 17 78 39 68 17 57
    91 71 52 38 17 14 91 43 58 50 27 29 48
    63 66 04 68 89 53 67 30 73 16 69 87 40 31
    04 62 98 27 23 09 70 98 73 93 38 53 60 04 23

    NOTE: As there are only 16384 routes, it is possible to solve this problem by
    trying every route. However, Problem 67, is the same challenge with a triangle
    containing one-hundred rows; it cannot be solved by brute force, and requires
    a clever method! ;o)

  Solution Approach:
    This problem can be approached using dynamic programming. Starting from the
    bottom of the triangle, compute the maximum total for each element by adding
    the maximum of the two adjacent numbers in the row below. This reduces the
    problem size iteratively until the top of the triangle is reached, which will
    contain the maximum total sum. Such a bottom-up approach avoids the need to
    explore all routes, making the solution efficient even for larger triangles.
    Implementing this method systematically will ensure an optimal and practical
    solution to the problem.

  Test Cases:
    preliminary:
      triangle_str=TRIANGLE_A,
      answer=23.

    main:
      triangle_str=TRIANGLE_B,
      answer=1074.


  Answer: 1074
  URL: https://projecteuler.net/problem=18
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.maths.graph_traversal import max_path_sum_triangle
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.utils.text_to_array import text2triangle

TRIANGLE_A = ('3\n'
              '7 4\n'
              '2 4 6\n'
              '8 5 9 3\n')
TRIANGLE_B = ('75\n'
              '95 64\n'
              '17 47 82\n'
              '18 35 87 10\n'
              '20 04 82 47 65\n'
              '19 01 23 75 03 34\n'
              '88 02 77 73 07 63 67\n'
              '99 65 04 28 06 16 70 92\n'
              '41 41 26 56 83 40 80 70 33\n'
              '41 48 72 33 47 32 37 16 94 29\n'
              '53 71 44 65 25 43 91 52 97 51 14\n'
              '70 11 33 28 77 73 17 78 39 68 17 57\n'
              '91 71 52 38 17 14 91 43 58 50 27 29 48\n'
              '63 66 04 68 89 53 67 30 73 16 69 87 40 31\n'
              '04 62 98 27 23 09 70 98 73 93 38 53 60 04 23\n')


@register_solution(euler_problem=18, test_case_category=TestCaseCategory.EXTENDED)
def maximum_path_sum_i(*, triangle_str: str) -> int:
    triangle_str = TRIANGLE_A if triangle_str == 'TRIANGLE_A' else TRIANGLE_B if triangle_str == 'TRIANGLE_B' else ''
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum_triangle(triangle)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=18, time_out_in_seconds=300, mode='evaluate'))
