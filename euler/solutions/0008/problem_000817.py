
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 817
# https://projecteuler.net/problem=817
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 817
    https://projecteuler.net/problem=817
    
Define $m = M(n, d)$ to be the smallest positive integer such that when $m^2$ is written in base $n$ it includes the base $n$ digit $d$. For example, $M(10,7) = 24$ because if all the squares are written out in base 10 the first time the digit 7 occurs is in $24^2 = 576$. $M(11,10) = 19$ as $19^2 = 361=2A9_{11}$.


Find $\displaystyle \sum_{d = 1}^{10^5}M(p, p - d)$ where $p = 10^9 + 7$.


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
