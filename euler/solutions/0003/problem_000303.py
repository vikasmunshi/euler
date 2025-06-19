#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 303
# https://projecteuler.net/problem=303
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
solution to Project Euler problem 303
https://projecteuler.net/problem=303

For a positive integer $n$, define $f(n)$ as the least positive multiple of $n$ that, written in base $10$, uses only digits $\le 2$.
Thus $f(2)=2$, $f(3)=12$, $f(7)=21$, $f(42)=210$, $f(89)=1121222$.
Also, $\sum \limits_{n = 1}^{100} {\dfrac{f(n)}{n}} = 11363107$.

Find $\sum \limits_{n=1}^{10000} {\dfrac{f(n)}{n}}$.



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