#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0082/p0082.py
  func: solve_path_sum_three_ways_p0082_s0
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


def reduce_column(matrix: list[list[int]], col: int) -> None:
    assert col > 0
    new_entries = [
        min(
            (
                sum((matrix[cell][col - 1] for cell in range(min(row, target), max(row, target) + 1)))
                + matrix[target][col]
                for target in range(len(matrix))
            )
        )
        for row in range(len(matrix))
    ]
    for row, value in enumerate(new_entries):
        matrix[row][col - 1] = value


def path_sum_three_ways(content: str) -> int:
    matrix: List[List[int]] = [[int(n) for n in line.split(",")] for line in content.splitlines(keepends=False) if line]
    for col in range(len(matrix) - 1, 0, -1):
        reduce_column(matrix, col)
    return min((matrix[row][0] for row in range(len(matrix))))


def get_text_file(url: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources" + "/" + url.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, file_url: str) -> int:
    content: str = get_text_file(file_url) if file_url else default
    return path_sum_three_ways(content)


def main() -> int:
    print(solve(file_url=str(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
