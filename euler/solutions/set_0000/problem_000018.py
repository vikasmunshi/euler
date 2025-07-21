# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 18: Maximum Path Sum I

Problem Statement:
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
However, Problem 67 is the same challenge with a triangle containing one-hundred rows;
it cannot be solved by brute force and requires a clever method! ;o)

Solution Approach:
Instead of pursuing a top-down approach that would require trying all possible paths (2^(n-1) paths
for an n-row triangle), we use dynamic programming with a bottom-up approach:

1. Key Insight: At each position, the maximum possible sum depends only on the maximum possible sums
   of the two adjacent positions in the row below.

2. Algorithm: Starting from the second-to-last row, replace each number with itself plus the maximum
   of the two adjacent numbers in the row below. After processing each row, the row below is no longer
   needed. By the time we reach the top, the single remaining value is our answer.

3. Complexity:
   - Time: O(n²) where n is the number of rows (proportional to the number of elements in the triangle)
   - Space: O(n²) to store the triangle, though the algorithm modifies it in-place

This dynamic programming approach is particularly important for solving the related Problem 67,
where a brute-force approach would require checking 2^99 possible paths—computationally infeasible.

The beauty of this approach is its simplicity and efficiency, transforming an exponential problem
into a linear one by recognizing the overlapping subproblems in path calculation.

URL: https://projecteuler.net/problem=18
Answer: 1074
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=18)
problem_number: int = 18

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'triangle_str': 'TRIANGLE_A'}, answer=23, ),
    ProblemArgs(kwargs={'triangle_str': 'TRIANGLE_B'}, answer=1074, ),
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
    Empty lines are ignored. The function parses the triangle text format used in
    Project Euler problems, handling any leading/trailing whitespace and empty lines.

    Implementation Details:
    1. Split the input text into lines
    2. Filter out empty lines
    3. For each line, split by spaces and convert each element to an integer
    4. Return the resulting nested list structure

    Args:
        text: String containing the triangle representation

    Returns:
        A list of lists where each inner list represents a row of the triangle

    Note:
        This function assumes well-formed input. Each row should have one more element
        than the row above it to form a proper triangle.
    """
    return [[int(num) for num in line.split(' ')] for line in text.splitlines() if line != '']


def max_path_sum(triangle: List[List[int]]) -> int:
    """Calculate the maximum path sum from top to bottom of a triangle.

    This function implements the utils dynamic programming algorithm used for both
    Problem 18 and Problem 67. It modifies the input triangle in-place to compute
    the maximum path sum with optimal efficiency.

    Algorithm:
    1. Starting from the second-to-last row, update each element by adding the maximum
       of the two adjacent elements from the row below
    2. Remove the last row after processing each row (as it's no longer needed)
    3. Continue until only one element remains at the top of the triangle
    4. This single element contains the maximum path sum

    Args:
        triangle: A nested list representing the triangle, where each inner list is a row

    Returns:
        The maximum path sum from top to bottom

    Time Complexity: O(n²) where n is the number of rows in the triangle
    Space Complexity: O(1) additional space (modifies the triangle in-place)
    """
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def max_path_sum_problem_18(*, triangle_str: str) -> int:
    """Find the maximum path sum from top to bottom of the given triangle.

    This solution uses a bottom-up dynamic programming approach that modifies the triangle in-place:

    Algorithm:
    1. Start from the second-to-last row of the triangle
    2. For each number in this row, add the maximum of the two adjacent numbers from the row below
       (i.e., triangle[-2][i] += max(triangle[-1][i], triangle[-1][i+1]))
    3. This transforms the second-to-last row into a new row containing partial maximum sums
    4. Remove the last row as it's no longer needed
    5. Repeat until only one row (with one number) remains
    6. The remaining number is the maximum path sum

    Theoretical Basis:
    The key insight is the optimal substructure property: the maximum path to any position
    depends only on the maximum paths to the two adjacent positions in the row below.
    This allows us to build the solution incrementally from bottom to top.

    Complexity Analysis:
    - Time Complexity: O(n²) where n is the number of rows in the triangle
      (we process each element once, and there are approximately n²/2 elements)
    - Space Complexity: O(n²) for storing the triangle, though we modify it in-place
      without requiring additional space proportional to the input size

    Compared to a naive recursive approach which would have O(2ⁿ) time complexity
    (as there are 2ⁿ⁻¹ possible paths from top to bottom), this solution is dramatically
    more efficient, especially for larger triangles.

    Args:
        triangle_str: Name of the triangle constant ('TRIANGLE_A' or 'TRIANGLE_B')
                      which will be evaluated to get the actual triangle text

    Returns:
        Maximum sum of any path from top to bottom of the triangle

    Example:
        >>> max_path_sum(triangle_str='TRIANGLE_A')  # The example triangle from the problem
        23  # Path: 3 → 7 → 4 → 9
    """
    triangle: List[List[int]] = text2triangle(eval(triangle_str))
    return max_path_sum(triangle)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
