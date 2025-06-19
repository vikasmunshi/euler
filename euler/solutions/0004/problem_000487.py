#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 487
# https://projecteuler.net/problem=487
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
solution to Project Euler problem 487
https://projecteuler.net/problem=487
Let $f_k(n)$ be the sum of the $k$th powers of the first $n$ positive integers.

For example, $f_2(10) = 1^2 + 2^2 + 3^2 + 4^2 + 5^2 + 6^2 + 7^2 + 8^2 + 9^2 + 10^2 = 385$.

Let $S_k(n)$ be the sum of $f_k(i)$ for $1 \le i \le n$. For example, $S_4(100) = 35375333830$.

What is $\sum (S_{10000}(10^{12}) \bmod p)$ over all primes $p$ between $2 \cdot 10^9$ and $2 \cdot 10^9 + 2000$?

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