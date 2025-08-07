#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 67: Maximum Path Sum Ii.

  Problem Statement:
    By starting at the top of the triangle below and moving to adjacent numbers on the
    row below, the maximum total from top to bottom is 23.

    3
    7 4
    2 4 6
    8 5 9 3

    That is, 3 + 7 + 4 + 9 = 23.

    Find the maximum total from top to bottom in triangle.txt
    (right click and 'Save Link/Target As...'), a 15K text file containing a triangle
    with one-hundred rows.

    NOTE: This is a much more difficult version of Problem 18. It is not possible to
    try every route to solve this problem, as there are 2 x 99 altogether! If you
    could check one trillion (10 x 12) routes every second it would take over twenty
    billion years to check them all. There is an efficient algorithm to solve it.

  Solution Approach:
    This problem requires finding the maximum sum path from the top to the bottom of
    a large triangle of numbers. Brute forcing all paths is computationally infeasible
    due to the exponential number of routes (2^99). Instead, an efficient approach is
    to use dynamic programming. Starting from the bottom row of the triangle, you can
    iteratively compute the maximum sum for each element by adding the maximum of the
    two adjacent numbers from the row below. By propagating these sums upward,
    eventually you compute the maximum total at the top. This technique leverages
    overlapping subproblems and optimal substructure to dramatically reduce
    computations. Implementing this bottom-up dynamic programming algorithm will
    efficiently solve the problem within a reasonable time frame.

  Test Cases:
    main:
      file_url=https://projecteuler.net/resources/documents/0067_triangle.txt,
      answer=7273.


  Answer: 7273
  URL: https://projecteuler.net/problem=67
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.maths.graph_traversal import max_path_sum_triangle
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.setup.cached_requests import get_text_file
from euler.utils.text_to_array import text2triangle


@register_solution(euler_problem=67, test_case_category=TestCaseCategory.EXTENDED)
def maximum_path_sum_ii(*, file_url: str) -> int:
    triangle_str: str = get_text_file(file_url)
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum_triangle(triangle)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=67, time_out_in_seconds=300, mode='evaluate'))
