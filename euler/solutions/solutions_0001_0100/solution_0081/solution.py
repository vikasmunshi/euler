#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 81: Path Sum Two Ways.

  Problem Statement:
    In the 5 by 5 matrix below, the minimal path sum from the top left to the
    bottom right, by only moving to the right and down, is indicated in bold
    red and is equal to 2427.

    Find the minimal path sum from the top left to the bottom right by only
    moving right and down in matrix.txt (right click and "Save Link/Target
    As..."), a 31K text file containing an 80 by 80 matrix.

  Solution Approach:
    To solve this problem, use dynamic programming to efficiently compute the
    minimal path sum. Start at the top-left cell and iteratively calculate the
    minimal sum to reach each cell by moving only right or down. For each cell,
    take the minimum of the sums from the cell above and the cell to the left,
    then add the current cell's value. Store these intermediate sums in a 2D
    array to avoid redundant calculations. Finally, the value at the bottom-right
    cell will represent the minimal path sum. This approach leverages the
    principle of optimality and ensures an O(n^2) time complexity for an n by n
    matrix.

  Test Cases:
    preliminary:
      file_url=,
      answer=2427.

    main:
      file_url=https://projecteuler.net/resources/documents/0081_matrix.txt,
      answer=427337.


  Answer: 427337
  URL: https://projecteuler.net/problem=81
"""
from __future__ import annotations

from typing import Generator, List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.utils.load_matrix import load_matrix


@register_solution(euler_problem=81, test_case_category=TestCaseCategory.EXTENDED)
def path_sum_two_ways(*, file_url: str) -> int:
    matrix: List[List[int]] = load_matrix(file_url)
    for row, col in move_diagonally((size := len(matrix))):
        neighbors = []
        if row < size - 1:
            neighbors.append(matrix[row + 1][col])
        if col < size - 1:
            neighbors.append(matrix[row][col + 1])
        matrix[row][col] += min(neighbors, default=0)
    return matrix[0][0]


def move_diagonally(size: int) -> Generator[tuple[int, int], None, None]:
    row, col = (size - 1, size - 1)
    while row >= 0:
        yield (row, col)
        row, col = (row - 1, col + 1)
        if row < 0:
            row, col = (col - 2, 0)
        if col >= size:
            col, row = (row, size - 1)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=81, time_out_in_seconds=300, mode='evaluate'))
