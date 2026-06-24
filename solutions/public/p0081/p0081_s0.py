#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 81: Path Sum: Two Ways [Level 2]. """
from __future__ import annotations

import typing

from solver.runners import runner

default: str = (
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n"
)


def move_diagonally(size: int) -> typing.Generator[tuple[int, int], None, None]:
    """Yield cell coordinates in reverse anti-diagonal order so each cell precedes its predecessors."""
    row, col = (size - 1, size - 1)
    while row >= 0:
        yield (row, col)
        row, col = (row - 1, col + 1)
        if row < 0:
            row, col = (col - 2, 0)
        if col >= size:
            col, row = (row, size - 1)


def path_sum_two_ways(content: str) -> int:
    """Accumulate the minimal cost to the bottom-right into each cell in topological order."""
    matrix: list[list[int]] = [[int(n) for n in line.split(",")] for line in content.splitlines(keepends=False) if line]
    for row, col in move_diagonally((size := len(matrix))):
        neighbors = []
        if row < size - 1:
            neighbors.append(matrix[row + 1][col])
        if col < size - 1:
            neighbors.append(matrix[row][col + 1])
        matrix[row][col] += min(neighbors, default=0)
    return matrix[0][0]


@runner.main
def solve(*args: str) -> str:
    """Minimum right/down path sum via in-place DP: each cell takes the smaller of its right and
    lower neighbour's finalised cost, swept over reverse anti-diagonals; O(N^2)."""
    file_url = args[0]

    content: str = runner.get_text_file(file_url) if file_url else default
    return str(path_sum_two_ways(content))


if __name__ == "__main__":
    raise SystemExit(solve())
