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

from typing import Any, List

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution
from euler_solver.utils.load_matrix import load_matrix

euler_problem: int = 83
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'file_url': ''}},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0083_matrix.txt'}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_path_sum_four_ways_p0083_s0(*, file_url: str) -> int:
    matrix: List[List[int]] = load_matrix(file_url)
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


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
