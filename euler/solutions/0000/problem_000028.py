#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 28
# https://projecteuler.net/problem=28
# Answer: answers={5: 101, 1001: 669171001}
# Notes: This solution uses a closed-form formula for finding the sum of spiral diagonals
# which is much more efficient than generating the full spiral.
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'size': 5},
        answer=101,
    ),
    ProblemArgs(
        kwargs={'size': 7},
        answer=261,
    ),
    ProblemArgs(
        kwargs={'size': 9},
        answer=537,
    ),
    ProblemArgs(
        kwargs={'size': 1001},
        answer=669171001,
    ),
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
    print(f'Generated spiral for size {size} with diagonal elements highlighted in\033[31m red\033[0m:')
    half_size = size // 2
    for row in range(half_size, -half_size - 1, -1):  # y-axis is inverted for display
        row_values = []
        for col in range(-half_size, half_size + 1):  # x-axis from left to right
            value = coordinate_map.get((col, row), 0)  # Get value at coordinate or 0 if not found
            # Highlight diagonal elements in red
            if col == row or col == -row:
                # Mark diagonal elements with an asterisk
                row_values.append(f"\033[31m{value:2d}\033[0m")
            else:
                row_values.append(f"{value:2d}")

        print(" ".join(row_values))

    diagonal_sum = sum(n for c, n in coordinate_map.items() if c[0] == c[1] or c[0] == -c[1])
    formula_result = ((size * (size * (4 * size + 3) + 8) - 9) // 6)
    print(f'{size=}; '
          f'{formula_result=}; '
          f'{diagonal_sum=}; '
          f'{"\033[32m✓\033[0m" if formula_result == diagonal_sum else "\033[31m✗\033[0m"}')
    return diagonal_sum


def solution(*, size: int) -> int:
    """Calculate the sum of diagonal elements in a number spiral using a closed-form formula.

    This is the optimized solution that directly calculates the sum using a mathematical formula
    derived from analyzing the pattern of diagonal numbers, without needing to generate the entire spiral.

    The closed-form formula is: (size * (size * (4 * size + 3) + 8) - 9) // 6

    This formula was derived by analyzing the pattern of numbers that appear on the diagonals and
    finding a mathematical relationship between the spiral size and the diagonal sum. The formula
    provides an O(1) time complexity solution compared to the O(n²) approach of generating the spiral.

    For small spirals (size <= 10), the function uses the number_spiral_with_diagonal_sum
    implementation which actually generates the spiral for visualization and verification purposes.
    For larger spirals where visualization is impractical, the efficient closed-form formula is used.

    Args:
        size: The width/height of the square spiral (must be odd)

    Returns:
        The sum of all numbers on both diagonals of the spiral
    """
    return (size * (size * (4 * size + 3) + 8) - 9) // 6 if size > 10 else number_spiral_with_diagonal_sum(size)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler Problem 28: Number Spiral Diagonals
https://projecteuler.net/problem=28

Problem Description:
Starting with the number 1 and moving to the right in a clockwise direction a 5 by 5 spiral is formed as follows:

21 22 23 24 25
20  7  8  9 10
19  6  1  2 11
18  5  4  3 12
17 16 15 14 13

It can be verified that the sum of the numbers on the diagonals is 101.
What is the sum of the numbers on the diagonals in a 1001 by 1001 spiral formed in the same way?

Mathematical Analysis:
By examining the spiral pattern, we can identify several key insights:

1. The corners of each "ring" of the spiral follow a pattern:
   - For a 3x3 spiral, the corners are 3, 5, 7, 9 (sum = 24 + center 1 = 25)
   - For a 5x5 spiral, the corners are 13, 17, 21, 25 (sum = 76 + previous sum 25 = 101)
   - For a 7x7 spiral, the corners are 31, 37, 43, 49 (sum = 160 + previous sum 101 = 261)

2. For each ring n (where n is odd):
   - The top-right corner value is n²
   - The other corners can be calculated as: n² - (n-1), n² - 2(n-1), n² - 3(n-1)

3. By summing these patterns, we derive the closed-form formula:
   - Diagonal sum = (size * (size * (4 * size + 3) + 8) - 9) // 6

Solution Approach:
This implementation provides two methods for solving the problem:

1. Closed-form Formula (Primary Solution):
   - Uses the mathematical formula derived from analyzing the diagonal patterns
   - Provides O(1) time complexity, making it efficient for large spirals
   - Formula: (size * (size * (4 * size + 3) + 8) - 9) // 6

2. Spiral Generation (Visualization & Verification):
   - For small spirals (size <= 10), generates the complete spiral matrix
   - Builds the spiral using a coordinate system with (0,0) at the center
   - Calculates adjacent positions based on minimizing distance from center
   - Visually displays the spiral with diagonal elements highlighted
   - Serves as verification for the mathematical formula

Diagonals Explanation:
The diagonal elements consist of:
1. The main diagonal (top-left to bottom-right): values where x = y
2. The anti-diagonal (top-right to bottom-left): values where x = -y
3. The center element (1) is counted only once despite being on both diagonals

For a 5x5 spiral, the diagonal elements are: 1, 3, 5, 7, 9, 13, 17, 21, 25
Their sum is 101, which matches our formula's result.

Performance Considerations:
The closed-form formula provides constant-time performance regardless of spiral size,
making it suitable for calculating the sum for the 1001x1001 spiral required by the problem.
The spiral generation approach is used only for small sizes to aid in understanding and verification.
''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
