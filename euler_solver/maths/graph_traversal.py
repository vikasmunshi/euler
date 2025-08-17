#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph traversal helpers

Utilities for solving classic path problems on small graphs used in Project
Euler problems. Currently provides an efficient solver for the maximum path sum
in a triangular grid using bottom-up dynamic programming. The implementation
operates on a deep-copied structure so the caller’s input is never mutated.

Public API
- max_path_sum_triangle(triangle): compute the maximum path sum from top to
  bottom in a triangle of integers.

Example
>>> from euler_solver.maths.graph_traversal import max_path_sum_triangle
>>> tri = [
...     [3],
...     [7, 4],
...     [2, 4, 6],
...     [8, 5, 9, 3],
... ]
>>> max_path_sum_triangle(tri)
23
"""
from __future__ import annotations

from copy import deepcopy
from typing import List


def max_path_sum_triangle(triangle: List[List[int]]) -> int:
    """
    Compute the maximum path sum in a triangle of integers.

    Starting at the top of the triangle, at each step you may move to one of the
    two adjacent numbers in the row below. This function returns the maximum
    possible sum along such a path. The input is deep-copied to avoid mutation.

    Args:
        triangle (List[List[int]]): Triangle represented as a list of rows, where
            row i has i+1 non-negative integers.

    Returns:
        int: The maximum sum achievable from top to bottom.

    Notes:
        - Complexity: O(n^2) time and O(n^2) space in the size of the triangle.
        - Non-mutating: operates on a deepcopy of the provided triangle.
    """
    triangle = deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]
