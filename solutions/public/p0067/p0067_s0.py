#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 67: Maximum Path Sum II [Level 1]. """
from __future__ import annotations

import copy

from solver.runners import runner


def text2triangle(text: str) -> list[list[int]]:
    """Parse whitespace-separated rows into a triangle; row i holds i+1 integers."""
    return [[int(num) for num in line.split(" ")] for line in text.splitlines() if line != ""]


def max_path_sum_triangle(triangle: list[list[int]]) -> int:
    """Bottom-up DP: fold each row into its parent by adding the larger child; O(n^2)."""
    triangle = copy.deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


@runner.main
def solve(*args: str) -> str:
    """Maximum top-to-base path sum via bottom-up triangle DP; O(n^2) in the row count."""
    file_url = args[0]

    triangle_str: str = runner.get_text_file(file_url)
    triangle: list[list[int]] = text2triangle(triangle_str)
    return str(max_path_sum_triangle(triangle))


if __name__ == "__main__":
    raise SystemExit(solve())
