#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 82: Path Sum: Three Ways [Level 3]. """
from __future__ import annotations

from solver.runners import runner

default: str = (
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n"
)


def reduce_column(matrix: list[list[int]], col: int) -> None:
    """Fold solved column col into col-1 so each entry holds the min cost to the right edge."""
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
    """Column-reduction DP: a vertical up/down detour is a range sum, so each column is a 1-D min; O(n^3)."""
    matrix: list[list[int]] = [[int(n) for n in line.split(",")] for line in content.splitlines(keepends=False) if line]
    for col in range(len(matrix) - 1, 0, -1):
        reduce_column(matrix, col)
    return min((matrix[row][0] for row in range(len(matrix))))


@runner.main
def solve(*args: str) -> str:
    """Column-reduction DP sweeping right to left; min over the reduced left column is the answer; O(n^3)."""
    file_url = args[0]

    content: str = runner.get_text_file(file_url) if file_url else default
    return str(path_sum_three_ways(content))


if __name__ == "__main__":
    raise SystemExit(solve())
