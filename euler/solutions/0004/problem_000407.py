#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 407
# https://projecteuler.net/problem=407
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
solution to Project Euler problem 407
https://projecteuler.net/problem=407

If we calculate $a^2 \bmod 6$ for $0 \leq a \leq 5$ we get: $0,1,4,3,4,1$.


The largest value of $a$ such that $a^2 \equiv a \bmod 6$ is $4$.

Let's call $M(n)$ the largest value of $a \lt n$ such that $a^2 \equiv a \pmod n$.

So $M(6) = 4$.


Find $\sum M(n)$ for $1 \leq n \leq 10^7$.



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