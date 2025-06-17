#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 15 - Lattice paths
# https://projecteuler.net/problem=15
# Answer: answers={2: 6, 20: 137846528820}
# Notes: Uses combinatorial solution based on binomial coefficient calculation
import textwrap
from math import factorial

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'lattice_size': 2},
        answer=6,
    ),
    ProblemArgs(
        kwargs={'lattice_size': 20},
        answer=137846528820,
    ),
]


def solution(*, lattice_size: int) -> int:
    """Calculate the number of routes through a square lattice of a given size.

    This uses the mathematical formula for combinations: C(2n,n) = (2n)!/(n!)²,
    which represents the number of ways to choose which n steps (out of 2n total steps)
    will be rightward movements (the remaining n steps will be downward).

    Args:
        lattice_size: Size of the square lattice (n×n grid has n+1 points on each side)

    Returns:
        The number of possible routes from top-left to bottom-right
    """
    return factorial(2 * lattice_size) // (factorial(lattice_size) ** 2)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 15: Lattice paths
https://projecteuler.net/problem=15

Problem Description:
Starting in the top left corner of a 2 * 2 grid, and only being able to move to the right and down,
there are exactly 6 routes to the bottom right corner.

How many such routes are there through a 20 * 20 grid?

Solution Approach:
- This is a classic combinatorial problem that can be solved using the binomial coefficient
- In an n×n grid, any path from top-left to bottom-right must use exactly n moves right and n moves down
- The total number of moves is always 2n (n right + n down)
- We need to choose which n positions out of the 2n total will be rightward moves
- This is equivalent to choosing n elements from 2n elements: C(2n,n) = (2n)!/(n!)²
- The formula gives us the number of ways to arrange n right moves and n down moves

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
