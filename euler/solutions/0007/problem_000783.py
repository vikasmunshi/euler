
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 783
# https://projecteuler.net/problem=783
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 783
    https://projecteuler.net/problem=783
    
Given $n$ and $k$ two positive integers we begin with an urn that contains $kn$ white balls. We then proceed through $n$ turns where on each turn $k$ black balls are added to the urn and then $2k$ random balls are removed from the urn.

We let $B_t(n,k)$ be the number of black balls that are removed on turn $t$.

Further define $E(n,k)$ as the expectation of $\displaystyle \sum_{t=1}^n B_t(n,k)^2$.

You are given $E(2,2) = 9.6$.

Find $E(10^6,10)$. Round your answer to the nearest whole number.


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
