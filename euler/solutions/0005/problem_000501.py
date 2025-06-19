#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 501
# https://projecteuler.net/problem=501
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
solution to Project Euler problem 501
https://projecteuler.net/problem=501
The eight divisors of $24$ are $1, 2, 3, 4, 6, 8, 12$ and $24$.
The ten numbers not exceeding $100$ having exactly eight divisors are $24, 30, 40, 42, 54, 56, 66, 70, 78$ and $88$.
Let $f(n)$ be the count of numbers not exceeding $n$ with exactly eight divisors.

You are given $f(100) = 10$, $f(1000) = 180$ and $f(10^6) = 224427$.

Find $f(10^{12})$.

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