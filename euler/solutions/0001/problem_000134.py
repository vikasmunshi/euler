
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 134
# https://projecteuler.net/problem=134
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 134
    https://projecteuler.net/problem=134
    Consider the consecutive primes $p_1 = 19$ and $p_2 = 23$. It can be verified that $1219$ is the smallest number such that the last digits are formed by $p_1$ whilst also being divisible by $p_2$.
In fact, with the exception of $p_1 = 3$ and $p_2 = 5$, for every pair of consecutive primes, $p_2 \gt p_1$, there exist values of $n$ for which the last digits are formed by $p_1$ and $n$ is divisible by $p_2$. Let $S$ be the smallest of these values of $n$.
Find $\sum S$ for every pair of consecutive primes with $5 \le p_1 \le 1000000$.


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
