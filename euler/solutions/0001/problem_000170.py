
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 170
# https://projecteuler.net/problem=170
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 170
    https://projecteuler.net/problem=170
    Take the number $6$ and multiply it by each of $1273$ and $9854$:

\begin{align}
6 \times 1273 &= 7638\\
6 \times 9854 &= 59124
\end{align}

By concatenating these products we get the $1$ to $9$ pandigital $763859124$. We will call $763859124$ the "concatenated product of $6$ and $(1273,9854)$". Notice too, that the concatenation of the input numbers, $612739854$, is also $1$ to $9$ pandigital.

The same can be done for $0$ to $9$ pandigital numbers.

What is the largest $0$ to $9$ pandigital $10$-digit concatenated product of an integer with two or more other integers, such that the concatenation of the input numbers is also a $0$ to $9$ pandigital $10$-digit number?

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
