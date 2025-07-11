# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 11: Largest Product in a Grid

Problem Statement:
In the 20×20 grid below, four numbers along a diagonal line have been marked in red.

08 02 22 97 38 15 00 40 00 75 04 05 07 78 52 12 50 77 91 08
49 49 99 40 17 81 18 57 60 87 17 40 98 43 69 48 04 56 62 00
81 49 31 73 55 79 14 29 93 71 40 67 53 88 30 03 49 13 36 65
52 70 95 23 04 60 11 42 69 24 68 56 01 32 56 71 37 02 36 91
22 31 16 71 51 67 63 89 41 92 36 54 22 40 40 28 66 33 13 80
24 47 32 60 99 03 45 02 44 75 33 53 78 36 84 20 35 17 12 50
32 98 81 28 64 23 67 10 26 38 40 67 59 54 70 66 18 38 64 70
67 26 20 68 02 62 12 20 95 63 94 39 63 08 40 91 66 49 94 21
24 55 58 05 66 73 99 26 97 17 78 78 96 83 14 88 34 89 63 72
21 36 23 09 75 00 76 44 20 45 35 14 00 61 33 97 34 31 33 95
78 17 53 28 22 75 31 67 15 94 03 80 04 62 16 14 09 53 56 92
16 39 05 42 96 35 31 47 55 58 88 24 00 17 54 24 36 29 85 57
86 56 00 48 35 71 89 07 05 44 44 37 44 60 21 58 51 54 17 58
19 80 81 68 05 94 47 69 28 73 92 13 86 52 17 77 04 89 55 40
04 52 08 83 97 35 99 16 07 97 57 32 16 26 26 79 33 27 98 66
88 36 68 87 57 62 20 72 03 46 33 67 46 55 12 32 63 93 53 69
04 42 16 73 38 25 39 11 24 94 72 18 08 46 29 32 40 62 76 36
20 69 36 41 72 30 23 88 34 62 99 69 82 67 59 85 74 04 36 16
20 73 35 29 78 31 90 01 74 31 49 71 48 86 81 16 23 57 05 54
01 70 54 71 83 51 54 69 16 92 33 48 61 43 52 01 89 19 67 48

The product of these numbers is 26 × 63 × 78 × 14 = 1788696.
What is the greatest product of four adjacent numbers in the same direction (up, down, left, right, or diagonally) in the 20×20 grid?

Solution Approach:
This solution employs a systematic approach to find the maximum product in the grid:

1. Grid Representation: The 20×20 grid is parsed into a 2D tuple structure for efficient access.

2. Directional Search: The algorithm simultaneously checks four directions for each starting position:
   - Horizontal (right): Product of num_adjacent consecutive numbers in a row
   - Vertical (down): Product of num_adjacent consecutive numbers in a column
   - Diagonal (down-right): Product of num_adjacent consecutive numbers in a diagonal
   - Diagonal (up-right): Product of num_adjacent consecutive numbers in the other diagonal

3. Optimized Iteration: Rather than using four separate loops for each direction, the solution
   calculates all four products in a single pass using a clever nested loop structure.

4. Functional Approach: The solution uses a compact, functional programming style with nested
   comprehensions to express the algorithm concisely.

The time complexity is O(n²k) where n is the grid dimension and k is num_adjacent,
as we check each possible starting position and calculate four products of length k for each.

Test Case:
- For num_adjacent=4: The maximum product is 70600674, which corresponds to the four adjacent
  numbers in the grid with the highest product.

URL: https://projecteuler.net/problem=11
Answer: 70600674
"""
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'num_adjacent': 4}, answer=70600674, ),
]
text_grid = """
    08 02 22 97 38 15 00 40 00 75 04 05 07 78 52 12 50 77 91 08
    49 49 99 40 17 81 18 57 60 87 17 40 98 43 69 48 04 56 62 00
    81 49 31 73 55 79 14 29 93 71 40 67 53 88 30 03 49 13 36 65
    52 70 95 23 04 60 11 42 69 24 68 56 01 32 56 71 37 02 36 91
    22 31 16 71 51 67 63 89 41 92 36 54 22 40 40 28 66 33 13 80
    24 47 32 60 99 03 45 02 44 75 33 53 78 36 84 20 35 17 12 50
    32 98 81 28 64 23 67 10 26 38 40 67 59 54 70 66 18 38 64 70
    67 26 20 68 02 62 12 20 95 63 94 39 63 08 40 91 66 49 94 21
    24 55 58 05 66 73 99 26 97 17 78 78 96 83 14 88 34 89 63 72
    21 36 23 09 75 00 76 44 20 45 35 14 00 61 33 97 34 31 33 95
    78 17 53 28 22 75 31 67 15 94 03 80 04 62 16 14 09 53 56 92
    16 39 05 42 96 35 31 47 55 58 88 24 00 17 54 24 36 29 85 57
    86 56 00 48 35 71 89 07 05 44 44 37 44 60 21 58 51 54 17 58
    19 80 81 68 05 94 47 69 28 73 92 13 86 52 17 77 04 89 55 40
    04 52 08 83 97 35 99 16 07 97 57 32 16 26 26 79 33 27 98 66
    88 36 68 87 57 62 20 72 03 46 33 67 46 55 12 32 63 93 53 69
    04 42 16 73 38 25 39 11 24 94 72 18 08 46 29 32 40 62 76 36
    20 69 36 41 72 30 23 88 34 62 99 69 82 67 59 85 74 04 36 16
    20 73 35 29 78 31 90 01 74 31 49 71 48 86 81 16 23 57 05 54
    01 70 54 71 83 51 54 69 16 92 33 48 61 43 52 01 89 19 67 48
    """
grid = tuple(tuple(int(num) for num in line.split()) for line in textwrap.dedent(text_grid.strip()).splitlines())
dimension_1 = len(grid)
dimension_2 = len(grid[0])


def solution(*, num_adjacent: int) -> int:
    """
    Find the greatest product of adjacent numbers in the 20×20 grid.

    This function calculates the maximum product of a specified number of adjacent
    cells in the grid, considering all four directions: horizontal, vertical,
    and both diagonals.

    Args:
        num_adjacent: The number of adjacent cells to consider for the product

    Returns:
        The maximum product found among all possible directions and starting positions

    Algorithm:
    1. For each valid starting position (x,y) in the grid:
       - Calculate the horizontal product (right from position)
       - Calculate the vertical product (down from position)
       - Calculate the diagonal product (down-right from position)
       - Calculate the anti-diagonal product (up-right from position)
    2. Return the maximum product found across all positions and directions

    Note: The implementation uses a functional approach with nested comprehensions and
    accumulating products through multiple iterations of the loop variables to calculate
    all four directional products simultaneously.

    Time Complexity: O(n²k) where n is the grid dimension and k is num_adjacent
    Space Complexity: O(1) as we only store the current maximum product
    """
    return max(max(horizontal, vertical, diagonal_1, diagonal_2)
               for x in range(dimension_1 - num_adjacent + 1)
               for y in range(dimension_2 - num_adjacent + 1)
               for horizontal, vertical, diagonal_1, diagonal_2 in ((1, 1, 1, 1),)
               for i in range(num_adjacent)
               for horizontal, vertical, diagonal_1, diagonal_2 in
               ((horizontal * grid[x][y + i],
                 vertical * grid[x + i][y],
                 diagonal_1 * grid[x + i][y + i],
                 diagonal_2 * grid[x + num_adjacent - 1 - i][y + i]),)
               )


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
