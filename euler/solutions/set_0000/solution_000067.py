#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 67: maximum_path_sum_ii

Problem Statement:
  By starting at the top of the triangle below and moving to adjacent numbers on
  the row below, the maximum total from top to bottom is 23. 37 4 2 4 6 8 5 9 3
  That is, 3 + 7 + 4 + 9 = 23. Find the maximum total from top to bottom in
  triangle.txt (right click and 'Save Link/Target As...'), a 15K text file
  containing a triangle with one-hundred rows. NOTE: This is a much more difficult
  version of Problem 18. It is not possible to try every route to solve this
  problem, as there are 299 altogether! If you could check one trillion (1012)
  routes every second it would take over twenty billion years to check them all.
  There is an efficient algorithm to solve it. ;o)

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=67
Answer: None
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase
from euler.setup.cached_requests import get_text_file
from euler.solutions.set_0000.solution_000018 import max_path_sum, text2triangle

test_cases: list[TestCase] = [
    TestCase(
        answer=7273,
        is_main_case=False,
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0067_triangle.txt'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #67
@register_solution(problem_number=67, test_cases=test_cases)
def maximum_path_sum_ii(*, file_url: str) -> int:
    """Find the maximum path sum from top to bottom of a large triangle from an external file.

    This solution handles the more challenging version of Problem 18, dealing with a triangle
    that has 100 rows instead of 15. Due to the scale of the problem (2^99 possible paths),
    it requires an efficient approach rather than brute-force checking of all paths.

    Implementation Details:
    1. Download the triangle data from the provided URL
    2. Parse the text into a nested list structure using text2triangle
    3. Calculate the maximum path sum using the dynamic programming approach
       implemented in the max_path_sum function from Problem 18

    The solution demonstrates code reuse and the application of dynamic programming
    to solve problems that would be computationally infeasible with naive approaches.

    Args:
        file_url: URL to the text file containing the triangle data

    Returns:
        Maximum sum of any path from top to bottom of the triangle

    Example:
        >>> maximum_path_sum_ii(file_url='https://projecteuler.net/resources/documents/0067_triangle.txt')
        7273
    """
    triangle_str: str = get_text_file(file_url)
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum(triangle)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(67))
