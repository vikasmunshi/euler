#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 82: path_sum_three_ways

Problem Statement:
  NOTE: This problem is a more challenging version of Problem 81. The minimal path
  sum in the 5 by 5 matrix below, by starting in any cell in the left column and
  finishing in any cell in the right column, and only moving up, down, and right,
  is indicated in red and bold; the sum is equal to 994.   \begin{pmatrix} 131 &
  673 & \color{red}{234} & \color{red}{103} & \color{red}{18}\\ \color{red}{201} &
  \color{red}{96} & \color{red}{342} & 965 & 150\\ 630 & 803 & 746 & 422 & 111\\
  537 & 699 & 497 & 121 & 956\\ 805 & 732 & 524 & 37 & 331 \end{pmatrix}   Find
  the minimal path sum from the left column to the right column in matrix.txt
  (right click and "Save Link/Target As..."), a 31K text file containing an 80 by
  80 matrix.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=82
Answer: None
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase
from euler.solutions.set_0000.solution_000081 import load_matrix

test_cases: list[TestCase] = [
    TestCase(
        answer=994,
        is_main_case=False,
        kwargs={'file_url': ''},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=260324,
        is_main_case=False,
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0082_matrix.txt'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #82
@register_solution(problem_number=82, test_cases=test_cases)
def path_sum_three_ways(*, file_url: str) -> int:
    """Find the minimal path sum through a matrix, moving only right, up, and down.

    This function calculates the minimum possible sum when traversing from any cell
    in the leftmost column to any cell in the rightmost column, with allowed movements
    being right, up, and down (but not left). It uses a dynamic programming approach
    with column-by-column processing.

    Args:
        file_url: URL to a text file containing a comma-separated matrix,
                 or None to use the example matrix from the problem statement

    Returns:
        The minimum path sum from any cell in the leftmost column to any cell in the rightmost column

    Algorithm details:
        1. Load the matrix from the file or use the example matrix
        2. Process columns from right to left using the reduce_column function
        3. After processing, the leftmost column contains the minimum path sums
        4. Return the minimum value in the leftmost column

    Time complexity: O(n³) where n is the size of the matrix (due to nested loops in reduce_column)
    Space complexity: O(n) additional space for temporary storage in reduce_column
    """
    # Load the matrix either from the provided URL or use the example matrix
    matrix: List[List[int]] = load_matrix(file_url)
    # Process columns from right to left
    for col in range(len(matrix) - 1, 0, -1):
        reduce_column(matrix, col)
    # The minimum value in the leftmost column is the answer
    return min(matrix[row][0] for row in range(len(matrix)))


def reduce_column(matrix: list[list[int]], col: int) -> None:
    """Compute minimum paths from previous column to current column.

    This function calculates the minimum path sum to reach each cell in column col-1
    by considering all possible paths that involve moving right from column col-1
    and then potentially moving up or down within column col.

    Args:
        matrix: The matrix containing the values and being modified in-place
        col: The current column being processed (must be > 0)

    The function modifies the matrix in-place, updating column col-1 with the
    minimum path sums to reach column col from column col-1.

    Algorithm details:
        1. For each row in column col-1, calculate the minimum path sum to any cell in column col
        2. This involves considering all cells in column col as potential targets
        3. For each target, calculate the sum of values in the path (including up/down movements)
        4. Update column col-1 with these minimum path sums
    """
    assert col > 0
    new_entries = [min(
        sum(matrix[cell][col - 1] for cell in range(min(row, target), max(row, target) + 1)) + matrix[target][col]
        for target in range(len(matrix)))
        for row in range(len(matrix))]
    for row, value in enumerate(new_entries):
        matrix[row][col - 1] = value


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(82))
