#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0083/p0083.py
  func: solve_path_sum_four_ways_p0083_s0
"""

from __future__ import annotations

from pathlib import Path
from sys import argv
from typing import List

default: str = (
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n"
)


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def path_sum_four_ways(content: str) -> int:
    matrix: List[List[int]] = [[int(n) for n in line.split(",")] for line in content.splitlines(keepends=False) if line]
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


def solve(*, file_url: str) -> int:
    content: str = get_text_file(file_url) if file_url else default
    return path_sum_four_ways(content)


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
