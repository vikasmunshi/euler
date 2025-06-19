
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 368
# https://projecteuler.net/problem=368
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 368
    https://projecteuler.net/problem=368
    The harmonic series $1 + \frac 1 2 + \frac 1 3 + \frac 1 4 + \cdots$ is well known to be divergent.

If we however omit from this series every term where the denominator has a $9$ in it, the series remarkably enough converges to approximately $22.9206766193$.

This modified harmonic series is called the Kempner series.

Let us now consider another modified harmonic series by omitting from the harmonic series every term where the denominator has $3$ or more equal consecutive digits.
One can verify that out of the first $1200$ terms of the harmonic series, only $20$ terms will be omitted.

These $20$ omitted terms are:
$$\frac 1 {111}, \frac 1 {222}, \frac 1 {333}, \frac 1 {444}, \frac 1 {555}, \frac 1 {666}, \frac 1 {777}, \frac 1 {888}, \frac 1 {999}, \frac 1 {1000}, \frac 1 {1110},$$
$$\frac 1 {1111}, \frac 1 {1112}, \frac 1 {1113}, \frac 1 {1114}, \frac 1 {1115}, \frac 1 {1116}, \frac 1 {1117}, \frac 1 {1118}, \frac 1 {1119}.$$

This series converges as well.

Find the value the series converges to.

Give your answer rounded to $10$ digits behind the decimal point.

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
