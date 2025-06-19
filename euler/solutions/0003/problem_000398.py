#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 398
# https://projecteuler.net/problem=398
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
solution to Project Euler problem 398
https://projecteuler.net/problem=398

Inside a rope of length $n$, $n - 1$ points are placed with distance $1$ from each other and from the endpoints. Among these points, we choose $m - 1$ points at random and cut the rope at these points to create $m$ segments.


Let $E(n, m)$ be the expected length of the second-shortest segment.
For example, $E(3, 2) = 2$ and $E(8, 3) = 16/7$.
Note that if multiple segments have the same shortest length the length of the second-shortest segment is defined as the same as the shortest length.


Find $E(10^7, 100)$.
Give your answer rounded to $5$ decimal places behind the decimal point.


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