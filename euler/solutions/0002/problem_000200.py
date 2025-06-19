
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 200
# https://projecteuler.net/problem=200
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 200
    https://projecteuler.net/problem=200
    We shall define a sqube to be a number of the form, $p^2 q^3$, where $p$ and $q$ are distinct primes.

For example, $200 = 5^2 2^3$ or $120072949 = 23^2 61^3$.

The first five squbes are $72, 108, 200, 392$, and $500$.

Interestingly, $200$ is also the first number for which you cannot change any single digit to make a prime; we shall call such numbers, prime-proof. The next prime-proof sqube which contains the contiguous sub-string "$200$" is $1992008$.

Find the $200$th prime-proof sqube containing the contiguous sub-string "$200$".

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
