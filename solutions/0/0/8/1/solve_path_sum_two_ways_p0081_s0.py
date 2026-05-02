#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0081/p0081.py
  func: solve_path_sum_two_ways_p0081_s0
"""

from __future__ import annotations

from pathlib import Path
from sys import argv
from typing import Generator, List


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


default: str = (
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n"
)


def move_diagonally(size: int) -> Generator[tuple[int, int], None, None]:
    row, col = (size - 1, size - 1)
    while row >= 0:
        yield (row, col)
        row, col = (row - 1, col + 1)
        if row < 0:
            row, col = (col - 2, 0)
        if col >= size:
            col, row = (row, size - 1)


def path_sum_two_ways(content: str) -> int:
    matrix: List[List[int]] = [[int(n) for n in line.split(",")] for line in content.splitlines(keepends=False) if line]
    for row, col in move_diagonally((size := len(matrix))):
        neighbors = []
        if row < size - 1:
            neighbors.append(matrix[row + 1][col])
        if col < size - 1:
            neighbors.append(matrix[row][col + 1])
        matrix[row][col] += min(neighbors, default=0)
    return matrix[0][0]


def solve(*, file_url: str) -> int:
    content: str = get_text_file(file_url) if file_url else default
    return path_sum_two_ways(content)


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
