#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 82: Path Sum Three Ways.

  Problem Statement:
    NOTE: This problem is a more challenging version of Problem 81.

    The minimal path sum in the 5 by 5 matrix below, by starting in any cell
    in the left column and finishing in any cell in the right column, and
    only moving up, down, and right, is indicated in red and bold; the sum is
    equal to 994.

        131  673  234  103   18
        201   96  342  965  150
        630  803  746  422  111
        537  699  497  121  956
        805  732  524   37  331

    Find the minimal path sum from the left column to the right column in
    matrix.txt (right click and "Save Link/Target As..."), a 31K text file
    containing an 80 by 80 matrix.

  Solution Approach:
    To solve this problem, consider dynamic programming techniques that
    enable efficient calculation of minimal path sums through a grid with
    restricted moves (up, down, right). You can represent each column as a
    state and iteratively update minimal costs to reach each cell by
    exploring possible paths from the previous column. Graph algorithms,
    such as shortest path computations in weighted directed acyclic graphs
    (DAGs), might also be useful, where nodes correspond to matrix cells and
    edges correspond to valid moves. Focus on optimizing the path cost from
    any cell in the leftmost column to any in the rightmost column efficiently.

  Test Cases:
    preliminary:
      file_url=,
      answer=994.

    main:
      file_url=https://projecteuler.net/resources/documents/0082_matrix.txt,
      answer=260324.


  Answer: 260324
  URL: https://projecteuler.net/problem=82
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.utils.load_matrix import load_matrix


@register_solution(euler_problem=82, test_case_category=TestCaseCategory.EXTENDED)
def path_sum_three_ways(*, file_url: str) -> int:
    matrix: List[List[int]] = load_matrix(file_url)
    for col in range(len(matrix) - 1, 0, -1):
        reduce_column(matrix, col)
    return min((matrix[row][0] for row in range(len(matrix))))


def reduce_column(matrix: list[list[int]], col: int) -> None:
    assert col > 0
    new_entries = [min((sum((matrix[cell][col - 1] for cell in range(min(row, target), max(row, target) + 1))) +
                        matrix[target][col] for target in range(len(matrix)))) for row in range(len(matrix))]
    for row, value in enumerate(new_entries):
        matrix[row][col - 1] = value


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=82, time_out_in_seconds=300, mode='evaluate'))
