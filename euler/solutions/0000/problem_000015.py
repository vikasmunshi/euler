# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 15: Lattice Paths

Problem Statement:
Starting in the top left corner of a 2×2 grid, and only being able to move to the right and down, 
there are exactly 6 routes to the bottom right corner.

[Visual representation of the 6 possible paths through a 2×2 grid]

How many such routes are there through a 20×20 grid?

Solution Approach:
This problem can be elegantly solved using combinatorial mathematics rather than through
enumeration or dynamic programming. The key insight is to recognize that:

1. In any valid path from the top-left to bottom-right corner of an n×n grid:
   - We must make exactly n moves to the right
   - We must make exactly n moves down
   - The total number of moves is always 2n (n right + n down)

2. Mathematical Formulation: This reduces to asking "in how many ways can we choose
   which n positions out of the 2n total moves will be right-moves?" This is exactly
   the binomial coefficient C(2n,n) = (2n)!/(n!)²

3. Implementation: We use the factorial function from Python's math module to calculate
   this coefficient directly, avoiding the need for explicit path enumeration or recursion.

This approach has O(n) time complexity (for calculating the factorials) and O(1) space
complexity, making it extremely efficient even for large grid sizes.

Test Cases:
- For a 2×2 grid: 6 possible routes
- For a 20×20 grid: 137,846,528,820 possible routes

Note: The factorial calculations can grow very large, but Python handles arbitrary precision
integers automatically, so we don't need to worry about overflow for the given problem size.

URL: https://projecteuler.net/problem=15
Answer: 137846528820
"""

from math import factorial

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'lattice_size': 2}, answer=6, ),
    ProblemArgs(kwargs={'lattice_size': 20}, answer=137846528820, ),
]


def solution(*, lattice_size: int) -> int:
    """Calculate the number of routes through a square lattice of a given size.

    This function computes the number of unique paths from the top-left corner to the 
    bottom-right corner of an n×n grid, where only rightward and downward movements are allowed.

    Mathematical Background:
    The problem reduces to a combination problem from discrete mathematics. For any path:
    - We need exactly n moves to the right and n moves down (total 2n moves)
    - The question becomes: "In how many ways can we choose which n positions out of 
      the 2n total will be right-moves?"
    - This is precisely the binomial coefficient C(2n,n) = (2n)!/(n!)²

    Args:
        lattice_size: Size of the square lattice (an n×n grid has n+1 points on each side)

    Returns:
        The number of possible routes from top-left to bottom-right corner

    Implementation Notes:
    - The solution uses Python's factorial function from the math module
    - The formula calculates exactly: (2n)!/(n!)²
    - Integer division (//) is used since the result is guaranteed to be an integer
    - For large values of n, the factorials grow very large, but Python handles 
      arbitrary-precision integers automatically

    Examples:
        >>> solution(lattice_size=1)
        2  # For a 1×1 grid: right-down or down-right
        >>> solution(lattice_size=2)
        6  # For a 2×2 grid: 6 distinct paths
    """
    return factorial(2 * lattice_size) // (factorial(lattice_size) ** 2)


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
