#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 621
# https://projecteuler.net/problem=621
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
solution to Project Euler problem 621
https://projecteuler.net/problem=621
Gauss famously proved that every positive integer can be expressed as the sum of three triangular numbers (including $0$ as the lowest triangular number). In fact most numbers can be expressed as a sum of three triangular numbers in several ways.

Let $G(n)$ be the number of ways of expressing $n$ as the sum of three triangular numbers, regarding different arrangements of the terms of the sum as distinct.

For example, $G(9) = 7$, as $9$ can be expressed as: $3+3+3$, $0+3+6$, $0+6+3$, $3+0+6$, $3+6+0$, $6+0+3$, $6+3+0$.
  
You are given $G(1000) = 78$ and $G(10^6) = 2106$.

Find $G(17526 \times 10^9)$.

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