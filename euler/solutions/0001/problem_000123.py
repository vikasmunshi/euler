
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 123
# https://projecteuler.net/problem=123
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 123
    https://projecteuler.net/problem=123
    Let $p_n$ be the $n$th prime: $2, 3, 5, 7, 11, ...$, and let $r$ be the remainder when $(p_n - 1)^n + (p_n + 1)^n$ is divided by $p_n^2$.
For example, when $n = 3$, $p_3 = 5$, and $4^3 + 6^3 = 280 \equiv 5 \mod 25$.
The least value of $n$ for which the remainder first exceeds $10^9$ is $7037$.
Find the least value of $n$ for which the remainder first exceeds $10^{10}$.


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
