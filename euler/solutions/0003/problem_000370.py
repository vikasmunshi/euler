
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 370
# https://projecteuler.net/problem=370
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 370
    https://projecteuler.net/problem=370
    Let us define a geometric triangle as an integer sided triangle with sides $a \le b \le c$ so that its sides form a geometric progression, i.e. $b^2 = a \cdot c$ 

An example of such a geometric triangle is the triangle with sides $a = 144$, $b = 156$ and $c = 169$.

There are $861805$ geometric triangles with perimeter $\le 10^6$.

How many geometric triangles exist with perimeter $\le 2.5 \cdot 10^{13}$?


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
