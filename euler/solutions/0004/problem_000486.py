#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 486
# https://projecteuler.net/problem=486
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
solution to Project Euler problem 486
https://projecteuler.net/problem=486
Let $F_5(n)$ be the number of strings $s$ such that:
$s$ consists only of '0's and '1's,
$s$ has length at most $n$, and
$s$ contains a palindromic substring of length at least $5$.
For example, $F_5(4) = 0$, $F_5(5) = 8$, 
$F_5(6) = 42$ and $F_5(11) = 3844$.

Let $D(L)$ be the number of integers $n$ such that $5 \le n \le L$ and $F_5(n)$ is divisible by $87654321$.

For example, $D(10^7) = 0$ and $D(5 \cdot 10^9) = 51$.

Find $D(10^{18})$.

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