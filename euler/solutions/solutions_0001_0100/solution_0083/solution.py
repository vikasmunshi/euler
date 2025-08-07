#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 83: Path Sum Four Ways.

  Problem Statement:
    NOTE: This problem is a significantly more challenging version of Problem 81.

    In the 5 by 5 matrix below, the minimal path sum from the top left to the
    bottom right, by moving left, right, up, and down, is indicated in bold red
    and is equal to 2297.

    Find the minimal path sum from the top left to the bottom right by moving
    left, right, up, and down in matrix.txt (right click and "Save Link/Target
    As..."), a 31K text file containing an 80 by 80 matrix.

  Solution Approach:
    To solve this problem, consider representing the matrix as a weighted graph
    where each cell is a node connected to its adjacent nodes (up, down, left,
    right). Use an efficient shortest path algorithm such as Dijkstra's algorithm
    to find the minimal path sum from the top-left node to the bottom-right node.
    Carefully manage the priority queue to handle the traversal cost and update
    distances as you explore neighbors. Efficient data structures and careful
    implementation will be essential due to the matrix size (80x80). Avoid brute
    force methods and focus on graph traversal techniques designed for weighted
    grids.

  Test Cases:
    preliminary:
      file_url=,
      answer=2297.

    main:
      file_url=https://projecteuler.net/resources/documents/0083_matrix.txt,
      answer=425185.


  Answer: 425185
  URL: https://projecteuler.net/problem=83
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.utils.load_matrix import load_matrix


@register_solution(euler_problem=83, test_case_category=TestCaseCategory.EXTENDED)
def path_sum_four_ways(*, file_url: str) -> int:
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
    raise SystemExit(evaluate(euler_problem=83, time_out_in_seconds=300, mode='evaluate'))
