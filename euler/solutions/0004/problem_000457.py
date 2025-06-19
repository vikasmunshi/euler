
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 457
# https://projecteuler.net/problem=457
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 457
    https://projecteuler.net/problem=457
    
Let $f(n) = n^2 - 3n - 1$.

Let $p$ be a prime.

Let $R(p)$ be the smallest positive integer $n$ such that $f(n) \bmod p^2 = 0$ if such an integer $n$ exists, otherwise $R(p) = 0$.


Let $SR(L)$ be $\sum R(p)$ for all primes not exceeding $L$.


Find $SR(10^7)$.


    """
    raise NotImplementedError


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
