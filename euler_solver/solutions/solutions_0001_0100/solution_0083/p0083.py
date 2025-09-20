#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 83: Path Sum: Four Ways.

Problem Statement:
    NOTE: This problem is a significantly more challenging version of Problem 81.

    In the 5 by 5 matrix below, the minimal path sum from the top left to the bottom
    right, by moving left, right, up, and down, is indicated in bold red and is equal
    to 2297.

        131   673   234   103    18
        201    96   342   965   150
        630   803   746   422   111
        537   699   497   121   956
        805   732   524    37   331

    Find the minimal path sum from the top left to the bottom right by moving left,
    right, up, and down in matrix.txt (right click and "Save Link/Target As..."), a
    31K text file containing an 80 by 80 matrix.

Solution Approach:
    Model the matrix as a weighted graph with nodes as cells and edges connecting
    adjacent cells in four directions. Use Dijkstra's algorithm or similar shortest
    path graph search techniques to find the minimal path sum efficiently. Time
    complexity roughly O(n^2 log n) for an n x n matrix, suitable for 80x80 input.

Answer: 425185
URL: https://projecteuler.net/problem=83
"""
from __future__ import annotations

from ctypes import c_char_p, c_longlong
from typing import Any, Callable, List

from euler_solver.framework import evaluate, get_text_file, import_c_lib, logger, register_solution, use_c_function

euler_problem: int = 83
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'file_url': ''},
     'answer': 2297},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0083_matrix.txt'},
     'answer': 425185},
]

default: str = ('131, 673, 234, 103, 18\n'
                '201, 96, 342, 965, 150\n'
                '630, 803, 746, 422, 111\n'
                '537, 699, 497, 121, 956\n'
                '805, 732, 524, 37, 331\n')


def c_wrapper() -> tuple[Callable, ...]:
    _c_lib = import_c_lib(euler_problem)
    # Bindings
    _path_sum_four_c = _c_lib.path_sum_four_ways_from_csv
    _path_sum_four_c.argtypes = [c_char_p]
    _path_sum_four_c.restype = c_longlong

    def path_sum_four_ways_c(content: str) -> int:
        """Compute minimal path sum with moves in four directions (Problem 83) from CSV matrix string."""
        return int(_path_sum_four_c(content.encode('utf-8')))

    return (path_sum_four_ways_c,)


@use_c_function(c_wrapper, 0)
def path_sum_four_ways(content: str) -> int:
    matrix: List[List[int]] = [[int(n) for n in line.split(',')] for line in content.splitlines(keepends=False) if line]
    size = len(matrix)
    node_weights = {(row, col): matrix[row][col] for row in range(size) for col in range(size)}
    infinity = sum(node_weights.values()) + 1
    unvisited = {(row, col) for row in range(size) for col in range(size)}
    distances = {(row, col): infinity for row in range(size) for col in range(size)}
    distances[0, 0] = matrix[0][0]
    target = (size - 1, size - 1)
    while target in unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        current_row, current_col = current
        up = (current_row - 1, current_col)
        down = (current_row + 1, current_col)
        left = (current_row, current_col - 1)
        right = (current_row, current_col + 1)
        for neighbor in [up, down, left, right]:
            neighbor_row, neighbor_col = neighbor
            if 0 <= neighbor_row < size and 0 <= neighbor_col < size and (neighbor in unvisited):
                new_distance = distances[current] + node_weights[neighbor]
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
        unvisited.remove(current)
    return distances[target]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_path_sum_four_ways_p0083_s0(*, file_url: str) -> int:
    content: str = get_text_file(file_url) if file_url else default
    return path_sum_four_ways(content)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
