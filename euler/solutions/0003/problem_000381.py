
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 381
# https://projecteuler.net/problem=381
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 381
    https://projecteuler.net/problem=381
    
For a prime $p$ let $S(p) = (\sum (p-k)!) \bmod (p)$ for $1 \le k \le 5$.


For example, if $p=7$,

$(7-1)! + (7-2)! + (7-3)! + (7-4)! + (7-5)! = 6! + 5! + 4! + 3! + 2! = 720+120+24+6+2 = 872$.
 
As $872 \bmod (7) = 4$, $S(7) = 4$.


It can be verified that $\sum S(p) = 480$ for $5 \le p \lt 100$.


Find $\sum S(p)$ for $5 \le p \lt 10^8$.





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
