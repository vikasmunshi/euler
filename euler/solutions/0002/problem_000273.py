#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 273
# https://projecteuler.net/problem=273
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
solution to Project Euler problem 273
https://projecteuler.net/problem=273
Consider equations of the form: $a^2 + b^2 = N$, $0 \le a \le b$, $a$, $b$ and $N$ integer.

For $N=65$ there are two solutions:
$a=1$, $b=8$ and $a=4$, $b=7$.
We call $S(N)$ the sum of the values of $a$ of all solutions of $a^2 + b^2 = N$, $0 \le a \le b$, $a$, $b$ and $N$ integer.
Thus $S(65) = 1 + 4 = 5$.
Find $\sum S(N)$, for all squarefree $N$ only divisible by primes of the form $4k+1$ with $4k+1 \lt 150$.


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