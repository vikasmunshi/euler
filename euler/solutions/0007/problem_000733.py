#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 733
# https://projecteuler.net/problem=733
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
solution to Project Euler problem 733
https://projecteuler.net/problem=733

Let $a_i$ be the sequence defined by $a_i=153^i \bmod 10\,000\,019$ for $i \ge 1$.

The first terms of $a_i$ are:
$153, 23409, 3581577, 7980255, 976697, 9434375, ...$


Consider the subsequences consisting of $4$ terms in ascending order. For the part of the sequence shown above, these are:

$153, 23409, 3581577, 7980255$

$153, 23409, 3581577, 9434375$

$153, 23409, 7980255, 9434375$

$153, 23409, 976697, 9434375$

$153, 3581577, 7980255, 9434375$ and

$23409, 3581577, 7980255, 9434375$.


Define $S(n)$ to be the sum of the terms for all such subsequences within the first $n$ terms of $a_i$. Thus $S(6)=94513710$.

You are given that $S(100)=4465488724217$.


Find $S(10^6)$ modulo $1\,000\,000\,007$.


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