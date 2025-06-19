
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 838
# https://projecteuler.net/problem=838
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 838
    https://projecteuler.net/problem=838
    Let $f(N)$ be the smallest positive integer that is not coprime to any positive integer $n \le N$ whose least significant digit is $3$.

For example $f(40)$ equals to $897 = 3 \cdot 13 \cdot 23$ since it is not coprime to any of $3,13,23,33$. By taking the natural logarithm (log to base $e$) we obtain $\ln f(40) = \ln 897 \approx 6.799056$ when rounded to six digits after the decimal point.

You are also given $\ln f(2800) \approx 715.019337$.

Find $f(10^6)$. Enter its natural logarithm rounded to six digits after the decimal point.

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
