
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 133
# https://projecteuler.net/problem=133
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 133
    https://projecteuler.net/problem=133
    A number consisting entirely of ones is called a repunit. We shall define $R(k)$ to be a repunit of length $k$; for example, $R(6) = 111111$.
Let us consider repunits of the form $R(10^n)$.
Although $R(10)$, $R(100)$, or $R(1000)$ are not divisible by $17$, $R(10000)$ is divisible by $17$. Yet there is no value of $n$ for which $R(10^n)$ will divide by $19$. In fact, it is remarkable that $11$, $17$, $41$, and $73$ are the only four primes below one-hundred that can  be a factor of $R(10^n)$.
Find the sum of all the primes below one-hundred thousand that will never be a factor of $R(10^n)$.


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
