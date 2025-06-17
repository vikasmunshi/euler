#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 18 - Maximum path sum I
# https://projecteuler.net/problem=18
# Answer: answers={'TRIANGLE_A': 23, 'TRIANGLE_B': 1074}
# Notes: Uses a bottom-up dynamic programming approach to find optimal paths
import textwrap
from typing import List

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'triangle_str': 'TRIANGLE_A'},
        answer=23,
    ),
    ProblemArgs(
        kwargs={'triangle_str': 'TRIANGLE_B'},
        answer=1074,
    ),
]

# Example triangle from the problem description
TRIANGLE_A = """
3
7 4
2 4 6
8 5 9 3
"""
# Main problem triangle to solve
TRIANGLE_B = """
75
95 64
17 47 82
18 35 87 10
20 04 82 47 65
19 01 23 75 03 34
88 02 77 73 07 63 67
99 65 04 28 06 16 70 92
41 41 26 56 83 40 80 70 33
41 48 72 33 47 32 37 16 94 29
53 71 44 65 25 43 91 52 97 51 14
70 11 33 28 77 73 17 78 39 68 17 57
91 71 52 38 17 14 91 43 58 50 27 29 48
63 66 04 68 89 53 67 30 73 16 69 87 40 31
04 62 98 27 23 09 70 98 73 93 38 53 60 04 23
"""


def text2triangle(text: str) -> List[List[int]]:
    """Convert a text representation of a triangle to a nested list of integers.

    The input text should have one row per line, with numbers separated by spaces.
    Empty lines are ignored.

    Args:
        text: String containing the triangle representation

    Returns:
        A list of lists where each inner list represents a row of the triangle
    """
    return [[int(num) for num in line.split(' ')] for line in text.splitlines() if line != '']


def solution(*, triangle_str: str) -> int:
    """Find the maximum path sum from top to bottom of the given triangle.

    This solution uses a bottom-up dynamic programming approach:
    1. Start from the second-to-last row of the triangle
    2. For each number in this row, add the maximum of the two adjacent numbers from the row below
    3. This transforms the second-to-last row into a new row containing partial maximum sums
    4. Remove the last row as it's no longer needed
    5. Repeat until only one row (with one number) remains
    6. The remaining number is the maximum path sum

    This approach has O(n) time complexity where n is the number of elements in the triangle,
    compared to O(2^n) for the brute force approach of checking all possible paths.

    Args:
        triangle_str: Name of the triangle constant ('TRIANGLE_A' or 'TRIANGLE_B')

    Returns:
        Maximum sum of any path from top to bottom of the triangle
    """
    triangle = text2triangle(eval(triangle_str))
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 18: Maximum path sum I
https://projecteuler.net/problem=18

Problem Description:
By starting at the top of the triangle below and moving to adjacent numbers on the row below,
the maximum total from top to bottom is 23.

3
7 4
2 4 6
8 5 9 3

That is, 3 + 7 + 4 + 9 = 23.

Find the maximum total from top to bottom of the triangle below:
75
95 64
17 47 82
18 35 87 10
20 04 82 47 65
19 01 23 75 03 34
88 02 77 73 07 63 67
99 65 04 28 06 16 70 92
41 41 26 56 83 40 80 70 33
41 48 72 33 47 32 37 16 94 29
53 71 44 65 25 43 91 52 97 51 14
70 11 33 28 77 73 17 78 39 68 17 57
91 71 52 38 17 14 91 43 58 50 27 29 48
63 66 04 68 89 53 67 30 73 16 69 87 40 31
04 62 98 27 23 09 70 98 73 93 38 53 60 04 23
NOTE: As there are only 16384 routes, it is possible to solve this problem by trying every route.
However, Problem 67, is the same challenge with a triangle containing one-hundred rows; it cannot be solved by brute
force, and requires a clever method! ;o)

Solution Approach:
- Instead of checking all possible paths from top to bottom (brute force),
  we use a bottom-up dynamic programming approach
- Starting from the bottom row, we work our way up the triangle
- For each position, we calculate the maximum possible sum that can be achieved
  by choosing the optimal path from that position downward
- This effectively "collapses" the triangle one row at a time
- By the time we reach the top, we have the maximum possible path sum
- This approach has O(n) time complexity, where n is the number of elements in the triangle

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
