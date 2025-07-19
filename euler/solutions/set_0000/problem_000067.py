# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 67:

Problem Statement:
By starting at the top of the triangle below and moving to adjacent numbers on the row below, the maximum total from
top to bottom is 23.

**3**
**7** 4

2 **4** 6

8 5 **9** 3

That is, 3 + 7 + 4 + 9 = 23.

Find the maximum total from top to bottom in triangle.txt (right click and 'Save Link/Target As...'), a 15K text file
containing a triangle with one-hundred rows.

**NOTE:** This is a much more difficult version of Problem 18.  It is not possible to try every route to solve this
problem, as there are 2⁹9 altogether! If you could check one trillion (10¹2) routes every second it would take over
twenty billion years to check them all. There is an efficient algorithm to solve it.;o)

Solution Approach:
This problem is a scaled-up version of Problem 18, containing a triangle with 100 rows instead of 15.
The key insight is that brute-force approaches (checking all possible paths) are computationally infeasible
as there are 2^99 possible paths.

We use the same dynamic programming approach as in Problem 18:
1. Start from the bottom row and work upward
2. For each element in a row, add the maximum of the two adjacent elements from the row below
3. By the time we reach the top, the single value contains the maximum path sum

This approach has O(n²) time complexity where n is the number of rows, making it efficient even for
a 100-row triangle. The implementation reuses the `max_path_sum` function from Problem 18, demonstrating
the power of dynamic programming to transform an exponential problem into a linear one.

Test Cases:
- For the provided 100-row triangle file, the maximum path sum is 7273

URL: https://projecteuler.net/problem=67
Answer: 7273
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.solutions.set_0000.problem_000018 import max_path_sum, text2triangle
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.cached_requests import get_text_file

# The problem number from Project Euler (https://projecteuler.net/problem=67)
problem_number: int = 67

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'file_url': 'https://projecteuler.net/resources/documents/0067_triangle.txt'}, answer=7273, ),
]


# Register this function as a solution for problem #67 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def max_path_sum_problem_67(*, file_url: str) -> int:
    """Find the maximum path sum from top to bottom of a large triangle from an external file.

    This solution handles the more challenging version of Problem 18, dealing with a triangle
    that has 100 rows instead of 15. Due to the scale of the problem (2^99 possible paths),
    it requires an efficient approach rather than brute-force checking of all paths.

    Implementation Details:
    1. Download the triangle data from the provided URL
    2. Parse the text into a nested list structure using text2triangle
    3. Calculate the maximum path sum using the dynamic programming approach
       implemented in the max_path_sum function from Problem 18

    The solution demonstrates code reuse and the application of dynamic programming
    to solve problems that would be computationally infeasible with naive approaches.

    Args:
        file_url: URL to the text file containing the triangle data

    Returns:
        Maximum sum of any path from top to bottom of the triangle

    Example:
        >>> max_path_sum_problem_67(file_url='https://projecteuler.net/resources/documents/0067_triangle.txt')
        7273
    """
    triangle_str: str = get_text_file(file_url)
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum(triangle)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
