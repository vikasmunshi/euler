
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 351
# https://projecteuler.net/problem=351
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 351
    https://projecteuler.net/problem=351
    A hexagonal orchard of order $n$ is a triangular lattice made up of points within a regular hexagon with side $n$. The following is an example of a hexagonal orchard of order $5$:







Highlighted in green are the points which are hidden from the center by a point closer to it. It can be seen that for a hexagonal orchard of order $5$, $30$ points are hidden from the center.



Let $H(n)$ be the number of points hidden from the center in a hexagonal orchard of order $n$.



$H(5) = 30$. $H(10) = 138$. $H(1\,000) = 1177848$.



Find $H(100\,000\,000)$.


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
