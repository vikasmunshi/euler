#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 402
# https://projecteuler.net/problem=402
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
solution to Project Euler problem 402
https://projecteuler.net/problem=402

It can be shown that the polynomial $n^4 + 4n^3 + 2n^2 + 5n$ is a multiple of $6$ for every integer $n$. It can also be shown that $6$ is the largest integer satisfying this property.


Define $M(a, b, c)$ as the maximum $m$ such that $n^4 + an^3 + bn^2 + cn$ is a multiple of $m$ for all integers $n$. For example, $M(4, 2, 5) = 6$.


Also, define $S(N)$ as the sum of $M(a, b, c)$ for all $0 \lt a, b, c \leq N$.


We can verify that $S(10) = 1972$ and $S(10000) = 2024258331114$.


Let $F_k$ be the Fibonacci sequence:

$F_0 = 0$, $F_1 = 1$ and

$F_k = F_{k-1} + F_{k-2}$ for $k \geq 2$.


Find the last $9$ digits of $\sum S(F_k)$ for $2 \leq k \leq 1234567890123$.


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