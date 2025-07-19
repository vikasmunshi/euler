#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 83:

Problem Statement:
NOTE: This problem is a significantly more challenging version of Problem 81.

In the 5 by 5 matrix below, the minimal path sum from the top left to the bottom right,
by moving left, right, up, and down, is indicated in bold red and is equal to 2297.


131  673  234  103  18
201  96  342  965  150
630  803  746  422  111
537  699  497  121  956
805  732  524  37  331


Find the minimal path sum from the top left to the bottom right by moving left, right, up, and down in
matrix.txt (right click and "Save Link/Target As..."), a 31K text file containing an 80 by 80 matrix.

Solution Approach:
1. Dijkstra's Algorithm for Pathfinding
   - This solution uses Dijkstra's algorithm to find the shortest path from the top-left to bottom-right cell.
   - Unlike problems 81 and 82, we can now move in all four directions (up, down, left, right).
   - Dijkstra's algorithm is ideal for this scenario as it guarantees the shortest path in a weighted graph.

2. Implementation Strategy
   - We treat the matrix as a graph where each cell is a node with connections to adjacent cells.
   - Each node has a weight equal to the value in the matrix.
   - We maintain two sets: unvisited nodes and distances from the start node.
   - In each iteration, we select the unvisited node with the minimum distance.
   - We update distances to its neighbors and mark it as visited.
   - We continue until we reach the target node (bottom-right).

3. Algorithm Details
   - Initialize all distances as infinity except the starting node (top-left)
   - While the target node is unvisited:
     - Select the unvisited node with minimum distance
     - Update distances to all of its unvisited neighbors
     - Mark the current node as visited
   - Return the final distance to the target node

Test Cases:
- Small 5x5 matrix (provided in the problem): Minimum path sum is 2297
- Large 80x80 matrix from file: Minimum path sum is 425185

URL: https://projecteuler.net/problem=83
Answer: 425185
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.solutions.set_0000.problem_000081 import load_matrix
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=83)
problem_number: int = 83

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': None}, answer=2297, ),
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0083_matrix.txt'}, answer=425185, ),
]


# Register this function as a solution for problem #83 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def min_path_four_directions(*, file_url: str | None) -> int:
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
    raise SystemExit(evaluate_solutions(problem_number))
