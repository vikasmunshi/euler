#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 405
# https://projecteuler.net/problem=405
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
solution to Project Euler problem 405
https://projecteuler.net/problem=405

We wish to tile a rectangle whose length is twice its width.

Let $T(0)$ be the tiling consisting of a single rectangle.

For $n \gt 0$, let $T(n)$ be obtained from $T(n-1)$ by replacing all tiles in the following manner:






The following animation demonstrates the tilings $T(n)$ for $n$ from $0$ to $5$:






Let $f(n)$ be the number of points where four tiles meet in $T(n)$.

For example, $f(1) = 0$, $f(4) = 82$ and $f(10^9) \bmod 17^7 = 126897180$.



Find $f(10^k)$ for $k = 10^{18}$, give your answer modulo $17^7$.


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