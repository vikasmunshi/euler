#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 81: Path Sum: Two Ways

Problem Statement:
In the 5 by 5 matrix below, the minimal path sum from the top left to the bottom right,
by only moving to the right and down, is indicated in bold red and is equal to 2427.

131  673  234  103  18
201  96   342  965  150
630  803  746  422  111
537  699  497  121  956
805  732  524  37   331

Find the minimal path sum from the top left to the bottom right by only moving right and down in
matrix.txt (right click and "Save Link/Target As..."), a 31K text file containing an 80 by 80 matrix.

Solution Approach:
1. Dynamic Programming with In-Place Matrix Modification
   - Rather than calculating all possible paths (which would be exponential),
     we use dynamic programming to build the minimum path sum to each cell.
   - We modify the matrix in-place to store the minimum path sum to reach each cell.
   - The final value at matrix[0][0] will represent the minimum path sum from start to end.

2. Diagonal Traversal Strategy
   - We traverse the matrix in a specific pattern using diagonal traversals.
   - Starting from the bottom-right cell, we work our way back to the top-left.
   - For each cell, we consider paths coming from the right and below,
     and choose the minimum of these paths.
   - This approach ensures we have all necessary information when processing each cell.

3. Implementation Details
   - The move_diagonally generator provides the sequence of coordinates to process.
   - We update each cell by adding the minimum value from its possible next steps.
   - For edge cells, we handle boundary conditions appropriately.
   - The matrix[0][0] value will ultimately contain the total minimum path sum.

Test Cases:
- Small 5x5 matrix (provided in the problem): Minimum path sum is 2427
- Large 80x80 matrix from file: Minimum path sum is 427337

URL: https://projecteuler.net/problem=81
Answer: 427337
"""
from typing import Generator, List

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.cached_requests import get_text_file

# The problem number from Project Euler (https://projecteuler.net/problem=81)
problem_number: int = 81

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': None}, answer=2427, ),
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0081_matrix.txt'}, answer=427337, ),
]


def load_matrix(file_url: str | None) -> List[List[int]]:
    # Load the matrix either from the provided URL or use the example matrix
    if file_url:
        content: str = get_text_file(file_url)
        matrix: List[List[int]] = [[int(n) for n in line.split(',')] for line in content.splitlines(keepends=False)]
    else:
        # Example matrix from the problem statement
        matrix = [[131, 673, 234, 103, 18],
                  [201, 96, 342, 965, 150],
                  [630, 803, 746, 422, 111],
                  [537, 699, 497, 121, 956],
                  [805, 732, 524, 37, 331]]
    return matrix


def move_diagonally(size: int) -> Generator[tuple[int, int], None, None]:
    """Generate coordinates for traversing a square matrix in a specific diagonal pattern.

    This generator yields coordinates (row, col) for traversing an NxN matrix starting from
    the bottom-right corner and working towards the top-left corner. The traversal follows
    a pattern of diagonals moving from lower-right to upper-left, ensuring that when computing
    minimum paths, each cell is processed after its right and bottom neighbors.

    The pattern ensures we can apply dynamic programming efficiently since each cell depends
    only on cells that have already been processed.

    Args:
        size: The size of the square matrix (number of rows/columns)

    Yields:
        Tuples of (row, col) coordinates in the traversal order

    Example for a 3x3 matrix:
        Yields coordinates in this order: (2,2), (1,2), (2,1), (0,2), (1,1), (2,0), (0,1), (1,0), (0,0)
    """
    row, col = size - 1, size - 1  # Start at bottom-right corner
    while row >= 0:
        yield row, col
        # Move diagonally up-right
        row, col = row - 1, col + 1
        # If we moved above the top row, wrap around
        if row < 0:
            row, col = col - 2, 0
        # If we moved beyond the rightmost column, wrap around
        if col >= size:
            col, row = row, size - 1


# Register this function as a solution for problem #81 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def min_path_diagonal(*, file_url: str | None) -> int:
    """Find the minimal path sum through a matrix, moving only right and down.

    This function calculates the minimum possible sum of values when traversing a matrix
    from the top-left corner to the bottom-right corner, with allowed movements only to the
    right or downward. It uses dynamic programming with in-place modification of the matrix
    to compute the solution efficiently.

    Args:
        file_url: URL to a text file containing a comma-separated matrix,
                 or None to use the example matrix from the problem statement

    Returns:
        The minimum path sum from top-left to bottom-right

    Algorithm details:
        1. Load the matrix from the file or use the example matrix
        2. Traverse the matrix diagonally from bottom-right to top-left
        3. For each cell, add the minimum of its right and bottom neighbors
        4. The value in the top-left cell (matrix[0][0]) gives the minimum path sum

    Time complexity: O(n²) where n is the matrix size
    Space complexity: O(1) additional space (in-place modification)
    """
    # Load the matrix either from the provided URL or use the example matrix
    matrix: List[List[int]] = load_matrix(file_url)

    # Process the matrix using dynamic programming
    for row, col in move_diagonally(size := len(matrix)):
        neighbors = []
        # Consider the cell below (if it exists)
        if row < size - 1:
            neighbors.append(matrix[row + 1][col])
        # Consider the cell to the right (if it exists)
        if col < size - 1:
            neighbors.append(matrix[row][col + 1])
        # Add the minimum of neighboring cells to the current cell
        # For the bottom-right cell, no neighbors exist so default to 0
        matrix[row][col] += min(neighbors, default=0)

    # The top-left cell now contains the minimum path sum
    return matrix[0][0]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
