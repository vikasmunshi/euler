
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 862
# https://projecteuler.net/problem=862
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 862
    https://projecteuler.net/problem=862
    
For a positive integer $n$ define $T(n)$ to be the number of strictly larger integers which can be formed by permuting the digits of $n$.


Leading zeros are not allowed and so for $n = 2302$ the total list of permutations would be:

$2023,2032,2203,2230,\mathbf{2302},2320,3022,32 02,3220$

giving $T(2302)=4$.


Further define $S(k)$ to be the sum of $T(n)$ for all $k$-digit numbers $n$. You are given $S(3) = 1701$.


Find $S(12)$.

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
