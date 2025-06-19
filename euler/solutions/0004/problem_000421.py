
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 421
# https://projecteuler.net/problem=421
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 421
    https://projecteuler.net/problem=421
    
Numbers of the form $n^{15}+1$ are composite for every integer $n \gt 1$.

For positive integers $n$ and $m$ let $s(n,m)$ be defined as the sum of the distinct prime factors of $n^{15}+1$ not exceeding $m$.

E.g. $2^{15}+1 = 3 \times 3 \times 11 \times 331$.

So $s(2,10) = 3$ and $s(2,1000) = 3+11+331 = 345$.



Also $10^{15}+1 = 7 \times 11 \times 13 \times 211 \times 241 \times 2161 \times 9091$.

So $s(10,100) = 31$ and $s(10,1000) = 483$.

Find $\sum s(n,10^8)$ for $1 \leq n \leq 10^{11}$.



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
