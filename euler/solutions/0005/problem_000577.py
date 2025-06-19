#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 577
# https://projecteuler.net/problem=577
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
solution to Project Euler problem 577
https://projecteuler.net/problem=577
An equilateral triangle with integer side length $n \ge 3$ is divided into $n^2$ equilateral triangles with side length 1 as shown in the diagram below.

The vertices of these triangles constitute a triangular lattice with $\frac{(n+1)(n+2)} 2$ lattice points.
Let $H(n)$ be the number of all regular hexagons that can be found by connecting 6 of these points. 





For example, $H(3)=1$, $H(6)=12$ and $H(20)=966$.

Find $\displaystyle \sum_{n=3}^{12345} H(n)$.

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