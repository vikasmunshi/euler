
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 884
# https://projecteuler.net/problem=884
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 884
    https://projecteuler.net/problem=884
    
Starting from a positive integer $n$, at each step we subtract from $n$ the largest perfect cube not exceeding $n$, until $n$ becomes $0$.

For example, with $n = 100$ the procedure ends in $4$ steps:
$$100 \xrightarrow{-4^3} 36 \xrightarrow{-3^3} 9 \xrightarrow{-2^3} 1 \xrightarrow{-1^3} 0.$$
Let $D(n)$ denote the number of steps of the procedure. Thus $D(100) = 4$.


Let $S(N)$ denote the sum of $D(n)$ for all positive integers $n$ strictly less than $N$.

For example, $S(100) = 512$.


Find $S(10^{17})$.

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
