#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 163
# https://projecteuler.net/problem=163
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
solution to Project Euler problem 163
https://projecteuler.net/problem=163
Consider an equilateral triangle in which straight lines are drawn from each vertex to the middle of the opposite side, such as in the size $1$ triangle in the sketch below.

Sixteen triangles of either different shape or size or orientation or location can now be observed in that triangle. Using size $1$ triangles as building blocks, larger triangles can be formed, such as the size $2$ triangle in the above sketch. One-hundred and four triangles of either different shape or size or orientation or location can now be observed in that size $2$ triangle.
It can be observed that the size $2$ triangle contains $4$ size $1$ triangle building blocks. A size $3$ triangle would contain $9$ size $1$ triangle building blocks and a size $n$ triangle would thus contain $n^2$ size $1$ triangle building blocks.
If we denote $T(n)$ as the number of triangles present in a triangle of size $n$, then
\begin{align}
T(1) &= 16\\
T(2) &= 104
\end{align}
Find $T(36)$.


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