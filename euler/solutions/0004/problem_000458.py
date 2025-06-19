
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 458
# https://projecteuler.net/problem=458
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 458
    https://projecteuler.net/problem=458
    
Consider the alphabet $A$ made out of the letters of the word "$\text{project}$": $A=\{\text c,\text e,\text j,\text o,\text p,\text r,\text t\}$.

Let $T(n)$ be the number of strings of length $n$ consisting of letters from $A$ that do not have a substring that is one of the $5040$ permutations of "$\text{project}$".

$T(7)=7^7-7!=818503$.


Find $T(10^{12})$. Give the last $9$ digits of your answer.




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
