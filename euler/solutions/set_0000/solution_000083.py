#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 83: path_sum_four_ways

Problem Statement:
  NOTE: This problem is a significantly more challenging version of Problem 81. In
  the 5 by 5 matrix below, the minimal path sum from the top left to the bottom
  right, by moving left, right, up, and down, is indicated in bold red and is
  equal to 2297.   \begin{pmatrix} \color{red}{131} & 673 & \color{red}{234} &
  \color{red}{103} & \color{red}{18}\\ \color{red}{201} & \color{red}{96} &
  \color{red}{342} & 965 & \color{red}{150}\\ 630 & 803 & 746 & \color{red}{422} &
  \color{red}{111}\\ 537 & 699 & 497 & \color{red}{121} & 956\\ 805 & 732 & 524 &
  \color{red}{37} & \color{red}{331} \end{pmatrix}   Find the minimal path sum
  from the top left to the bottom right by moving left, right, up, and down in
  matrix.txt (right click and "Save Link/Target As..."), a 31K text file
  containing an 80 by 80 matrix.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=83
Answer: None
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase
from euler.solutions.set_0000.solution_000081 import load_matrix

test_cases: list[TestCase] = [
    TestCase(
        answer=2297,
        is_main_case=False,
        kwargs={'file_url': ''},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=425185,
        is_main_case=False,
        kwargs={'file_url': 'https://projecteuler.net/resources/documents/0083_matrix.txt'},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #83
@register_solution(problem_number=83, test_cases=test_cases)
def path_sum_four_ways(*, file_url: str) -> int:
    """
    Find the minimal path sum through a matrix, moving in all four directions.

    This function implements Dijkstra's algorithm to find the shortest path from the top-left
    corner to the bottom-right corner of a matrix, with allowed movements in all four
    directions: up, down, left, and right. The path sum includes both the starting and
    ending cells.

    Args:
        file_url: URL to a text file containing a comma-separated matrix,
                 or None to use the example matrix from the problem statement

    Returns:
        The minimum path sum from top-left to bottom-right

    Algorithm details:
        1. Initialize distances to all nodes as infinity except the starting node
        2. While the target node is unvisited:
           a. Select the unvisited node with minimum distance
           b. For each neighbor (up, down, left, right):
              i. Update its distance if a shorter path is found
           c. Mark the current node as visited
        3. Return the final distance to the target node

    Time complexity: O(n² log n) where n is the matrix size
    Space complexity: O(n²) for the distance and unvisited sets
    """
    # Load the matrix either from the provided URL or use the example matrix
    matrix: List[List[int]] = load_matrix(file_url)
    size = len(matrix)

    # Create a dictionary mapping coordinates to cell values
    node_weights = {(row, col): matrix[row][col] for row in range(size) for col in range(size)}

    # Initialize algorithm variables
    infinity = sum(node_weights.values()) + 1  # Value larger than any possible path sum
    unvisited = {(row, col) for row in range(size) for col in range(size)}  # All nodes start as unvisited
    distances = {(row, col): infinity for row in range(size) for col in
                 range(size)}  # Initialize all distances as infinity
    distances[(0, 0)] = matrix[0][0]  # Distance to starting node is its own value
    target = (size - 1, size - 1)  # Bottom-right cell

    # Dijkstra's algorithm main loop
    while target in unvisited:
        # Find unvisited node with minimum distance
        current = min(unvisited, key=lambda node: distances[node])
        current_row, current_col = current

        # Define the four possible neighbors (up, down, left, right)
        up = (current_row - 1, current_col)
        down = (current_row + 1, current_col)
        left = (current_row, current_col - 1)
        right = (current_row, current_col + 1)

        # Update distances to neighbors if they're still unvisited and valid matrix positions
        for neighbor in [up, down, left, right]:
            neighbor_row, neighbor_col = neighbor
            # Check if neighbor is a valid position in the matrix
            if 0 <= neighbor_row < size and 0 <= neighbor_col < size and neighbor in unvisited:
                # Update distance if a shorter path is found
                new_distance = distances[current] + node_weights[neighbor]
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance

        # Mark current node as visited
        unvisited.remove(current)

    return distances[target]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(83))
