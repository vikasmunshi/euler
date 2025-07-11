#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 28: Number spiral diagonals

Problem Statement:
Starting with the number 1 and moving to the right in a clockwise direction a 5 by 5 spiral
is formed as follows:

21 22 23 24 25
20  7  8  9 10
19  6  1  2 11
18  5  4  3 12
17 16 15 14 13

It can be verified that the sum of the numbers on the diagonals is 101.

What is the sum of the numbers on the diagonals in a 1001 by 1001 spiral formed in the same way?

Solution Approach:
This implementation offers two approaches to solve the problem:

1. Visualization approach: For small spirals (size ≤ 10), the solution generates the actual
   spiral and calculates the diagonal sum by traversing the coordinates. This provides
   a visual verification of the pattern and the diagonal elements.

2. Mathematical approach: For larger spirals, the solution uses a closed-form formula
   derived from analyzing the pattern of diagonal numbers. The formula provides an O(1)
   time complexity solution: (size * (size * (4 * size + 3) + 8) - 9) // 6

Test Cases:
- For size=5, the answer is 101
- For size=7, the answer is 261
- For size=9, the answer is 537
- For size=1001, the answer is 669,171,001

URL: https://projecteuler.net/problem=28
Answer: 669171001
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'size': 5}, answer=101, ),
    ProblemArgs(kwargs={'size': 7}, answer=261, ),
    ProblemArgs(kwargs={'size': 9}, answer=537, ),
    ProblemArgs(kwargs={'size': 1001}, answer=669171001, ),
]


def number_spiral_with_diagonal_sum(size: int) -> int:
    """Calculate the sum of diagonal elements in a number spiral of a given size.

    This function generates a spiral of numbers in a square grid, starting with 1 at the center
    position (0,0) and spiraling outward in a clockwise direction. It constructs the spiral
    by placing each successive number in the adjacent position that minimizes the distance
    from the center, creating the classic spiral pattern.

    The algorithm works by:
    1. Starting with 1 at coordinate (0,0)
    2. For each subsequent number, finding the next available adjacent position
       (right, down, left, or up) that is closest to the center
    3. Placing the number at that position and continuing until the spiral is complete
    4. Summing the numbers that appear on both diagonals (northwest-southeast and
       northeast-southwest)

    The visualization displays the spiral in a square grid with the diagonals highlighted
    in red for easy identification. The function also compares the calculated sum with
    the result from the closed-form formula to verify correctness.

    Args:
        size: The width/height of the square spiral (must be odd)

    Returns:
        The sum of all numbers on both diagonals of the spiral

    Example:
        For size=5, the function will generate and print the spiral as:
        21 22 23 24 25
        20  7  8  9 10
        19  6  1  2 11
        18  5  4  3 12
        17 16 15 14 13

        Where the diagonal elements (21, 7, 1, 3, 13, 9, 5, 17, 25) appear in red when displayed
        in a terminal that supports ANSI color codes.
    """
    x, y, coordinate_map = 0, 0, {(0, 0): 1}
    for number in range(2, size ** 2 + 1):
        free_adjacent_coords = (c for c in ((x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)) if c not in coordinate_map)
        x, y = min(((c[0] ** 2 + c[1] ** 2, c) for c in free_adjacent_coords), key=lambda c: c[0])[1]
        coordinate_map[(x, y)] = number

    # Print the coordinate map in a spiral format
    # Set orange color code (\033[33m for orange/yellow)
    msg: List[str] = [f'Generated spiral for size {size} with diagonal elements highlighted in\033[34m blue\033[0m:']
    half_size = size // 2
    for row in range(half_size, -half_size - 1, -1):  # y-axis is inverted for display
        row_values = []
        for col in range(-half_size, half_size + 1):  # x-axis from left to right
            value = coordinate_map.get((col, row), 0)  # Get value at coordinate or 0 if not found
            # Highlight diagonal elements in red
            if col == row or col == -row:
                # Mark diagonal elements with blue color
                row_values.append(f"\033[34m{value:2d}\033[0m")
            else:
                row_values.append(f"{value:2d}")
        msg.append(' '.join(row_values))
    diagonal_sum = sum(n for c, n in coordinate_map.items() if c[0] == c[1] or c[0] == -c[1])
    formula_result = ((size * (size * (4 * size + 3) + 8) - 9) // 6)
    status = '\033[32m✓' if formula_result == diagonal_sum else '\033[31m✗'
    msg.append(f'{status} {size=}; {formula_result=}; {diagonal_sum=}\033[0m')
    print('\n'.join(msg))
    return diagonal_sum


def solution(*, size: int) -> int:
    """Calculate the sum of diagonal elements in a number spiral using a closed-form formula.

    This solution efficiently calculates the sum of diagonal elements in a square number spiral
    without generating the entire spiral. For small spirals (size ≤ 10), it uses the visual
    approach for demonstration purposes. For larger spirals, it applies the derived mathematical
    formula for optimal performance.

    Args:
        size: The width/height of the square spiral (must be odd)

    Returns:
        The sum of all numbers on both diagonals of the spiral

    Raises:
        ValueError: If size is not a positive odd integer

    Example:
        >>> solution(size=5)
        101
        >>> solution(size=1001)
        669171001
    """
    if not isinstance(size, int) or size <= 0 or size % 2 == 0:
        raise ValueError("Size must be a positive odd integer")

    return (size * (size * (4 * size + 3) + 8) - 9) // 6 if size > 10 else number_spiral_with_diagonal_sum(size)


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast, List
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
