
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 784
# https://projecteuler.net/problem=784
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 784
    https://projecteuler.net/problem=784
    
Let's call a pair of positive integers $p$, $q$ ($p \lt q$) reciprocal, if there is a positive integer $r\lt p$ such that $r$ equals both the inverse of $p$ modulo $q$ and the inverse of $q$ modulo $p$.


For example, $(3,5)$ is one reciprocal pair for $r=2$.

Let $F(N)$ be the total sum of $p+q$ for all reciprocal pairs $(p,q)$ where $p \le N$.


$F(5)=59$ due to these four reciprocal pairs $(3,5)$, $(4,11)$, $(5,7)$ and $(5,19)$.

You are also given $F(10^2) = 697317$.


Find $F(2\cdot 10^6)$.

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
