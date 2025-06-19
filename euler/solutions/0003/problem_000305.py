#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 305
# https://projecteuler.net/problem=305
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
solution to Project Euler problem 305
https://projecteuler.net/problem=305

Let's call $S$ the (infinite) string that is made by concatenating the consecutive positive integers (starting from $1$)  written down in base $10$.
 
Thus, $S = 1234567891011121314151617181920212223242\cdots$


It's easy to see that any number will show up an infinite number of times in $S$.


Let's call $f(n)$ the starting position of the $n$th occurrence of $n$ in $S$.
 
For example, $f(1)=1$, $f(5)=81$, $f(12)=271$ and $f(7780)=111111365$.


Find $\sum f(3^k)$ for $1 \le k \le 13$.



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