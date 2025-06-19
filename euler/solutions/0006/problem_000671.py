#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 671
# https://projecteuler.net/problem=671
# Answer: 
# Notes: 
import textwrap
from typing import Any, Dict

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(**kwarg: Dict[str, Any]) -> SolutionResult:
    # enter the solution here
    raise NotImplementedError


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 671
https://projecteuler.net/problem=671
A certain type of flexible tile comes in three different sizes - $1 \times 1$, $1 \times 2$, and $1 \times 3$ - and in $k$ different colours. There is an unlimited number of tiles available in each combination of size and colour.

These are used to tile a closed loop of width $2$ and length (circumference) $n$, where $n$ is a positive integer, subject to the following conditions:

The loop must be fully covered by non-overlapping tiles.
It is not permitted for four tiles to have their corners meeting at a single point.
Adjacent tiles must be of different colours.


For example, the following is an acceptable tiling of a $2\times 23$ loop with $k=4$ (blue, green, red and yellow):





but the following is not an acceptable tiling, because it violates the "no four corners meeting at a point" rule:





Let $F_k(n)$ be the number of ways the $2\times n$ loop can be tiled subject to these rules when $k$ colours are available. (Not all $k$ colours have to be used.) Where reflecting horizontally or vertically would give a different tiling, these tilings are to be counted separately.

For example, $F_4(3) = 104$, $F_5(7) = 3327300$, and $F_6(101)\equiv 75309980 \pmod{1\,000\,004\,321}$.
Find $F_{10}(10\,004\,003\,002\,001) \bmod 1\,000\,004\,321$.


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