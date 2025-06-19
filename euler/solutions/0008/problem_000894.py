#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 894
# https://projecteuler.net/problem=894
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
solution to Project Euler problem 894
https://projecteuler.net/problem=894
Consider a unit circlecircle with radius 1 $C_0$ on the plane that does not enclose the origin. For $k\ge 1$, a circle $C_k$ is created by scaling and rotating $C_{k - 1}$ with respect to the origin. That is, both the radius and the distance to the origin are scaled by the same factor, and the centre of rotation is the origin. The scaling factor is positive and strictly less than one. Both it and the rotation angle remain constant for each $k$.

It is given that $C_0$ is externally tangent to $C_1$, $C_7$ and $C_8$, as shown in the diagram below, and no two circles overlap.


Find the total area of all the circular trianglesA circular triangle is a triangle with circular arc edges in the diagram, i.e. the area painted green above.

Give your answer rounded to $10$ places after the decimal point.

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