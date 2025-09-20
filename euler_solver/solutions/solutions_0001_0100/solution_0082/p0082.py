#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 82: Path Sum: Three Ways.

Problem Statement:
    NOTE: This problem is a more challenging version of Problem 81.

    The minimal path sum in the 5 by 5 matrix below, by starting in any cell in the left
    column and finishing in any cell in the right column, and only moving up, down, and right,
    is indicated in red and bold; the sum is equal to 994.

        131   673   234   103    18
        201    96   342   965   150
        630   803   746   422   111
        537   699   497   121   956
        805   732   524    37   331

    Find the minimal path sum from the left column to the right column in matrix.txt
    (right click and "Save Link/Target As..."), a 31K text file containing an 80 by 80 matrix.

Solution Approach:
    Model the problem as a shortest path in a directed graph where each cell connects to the
    cell to the right and moves up/down within columns. Use dynamic programming or Dijkstra's
    algorithm column by column to compute minimal path sums. Time complexity roughly O(n^2).

Answer: 260324
URL: https://projecteuler.net/problem=82
"""
from __future__ import annotations

from ctypes import c_char_p, c_longlong
from typing import Any, Callable, List

from euler_solver.framework import evaluate, get_text_file, import_c_lib, logger, register_solution, use_c_function

euler_problem: int = 82
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'file_url': ''},
     'answer': 994},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0082_matrix.txt'},
     'answer': 260324},
]

default: str = ('131, 673, 234, 103, 18\n'
                '201, 96, 342, 965, 150\n'
                '630, 803, 746, 422, 111\n'
                '537, 699, 497, 121, 956\n'
                '805, 732, 524, 37, 331\n')


def c_wrapper() -> tuple[Callable, ...]:
    _c_lib = import_c_lib(euler_problem)
    # Bindings
    _path_sum_three_c = _c_lib.path_sum_three_ways_from_csv
    _path_sum_three_c.argtypes = [c_char_p]
    _path_sum_three_c.restype = c_longlong

    def path_sum_three_ways_c(content: str) -> int:
        """Compute minimal path sum with moves up/down/right (Problem 82) from CSV matrix string."""
        return int(_path_sum_three_c(content.encode('utf-8')))

    return (path_sum_three_ways_c,)


@use_c_function(c_wrapper, 0)
def path_sum_three_ways(content: str) -> int:
    matrix: List[List[int]] = [[int(n) for n in line.split(',')] for line in content.splitlines(keepends=False) if line]
    for col in range(len(matrix) - 1, 0, -1):
        reduce_column(matrix, col)
    return min((matrix[row][0] for row in range(len(matrix))))


def reduce_column(matrix: list[list[int]], col: int) -> None:
    assert col > 0
    new_entries = [min((sum((matrix[cell][col - 1] for cell in range(min(row, target), max(row, target) + 1))) +
                        matrix[target][col] for target in range(len(matrix)))) for row in range(len(matrix))]
    for row, value in enumerate(new_entries):
        matrix[row][col - 1] = value


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_path_sum_three_ways_p0082_s0(*, file_url: str) -> int:
    content: str = get_text_file(file_url) if file_url else default
    return path_sum_three_ways(content)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
