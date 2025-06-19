
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 539
# https://projecteuler.net/problem=539
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 539
    https://projecteuler.net/problem=539
    
Start from an ordered list of all integers from $1$ to $n$. Going from left to right, remove the first number and every other number afterward until the end of the list. Repeat the procedure from right to left, removing the right most number and every other number from the numbers left. Continue removing every other numbers, alternating left to right and right to left, until a single number remains.


Starting with $n = 9$, we have:

$\underline 1\,2\,\underline 3\,4\,\underline 5\,6\,\underline 7\,8\,\underline 9$

$2\,\underline 4\,6\,\underline 8$

$\underline 2\,6$

$6$


Let $P(n)$ be the last number left starting with a list of length $n$.

Let $\displaystyle S(n) = \sum_{k=1}^n P(k)$.

You are given $P(1)=1$, $P(9) = 6$, $P(1000)=510$, $S(1000)=268271$.


Find $S(10^{18}) \bmod 987654321$.


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
