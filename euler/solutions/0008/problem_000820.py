
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 820
# https://projecteuler.net/problem=820
# Answer: 
# Notes: 
from typing import cast, Any

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(*, kwarg: Any) -> SolutionResult:
    r"""
    solution to Project Euler problem 820
    https://projecteuler.net/problem=820
    Let $d_n(x)$ be the $n$th decimal digit of the fractional part of $x$, or $0$ if the fractional part has fewer than $n$ digits.
For example:

$d_7 \mathopen{}\left( 1 \right)\mathclose{} = d_7 \mathopen{}\left( \frac 1 2 \right)\mathclose{} = d_7 \mathopen{}\left( \frac 1 4 \right)\mathclose{} = d_7 \mathopen{}\left( \frac 1 5 \right)\mathclose{} = 0$
$d_7 \mathopen{}\left( \frac 1 3 \right)\mathclose{} = 3$ since $\frac 1 3 =$ 0.3333333333...
$d_7 \mathopen{}\left( \frac 1 6 \right)\mathclose{} = 6$ since $\frac 1 6 =$ 0.1666666666...
$d_7 \mathopen{}\left( \frac 1 7 \right)\mathclose{} = 1$ since $\frac 1 7 =$ 0.1428571428...

Let $\displaystyle  S(n) = \sum_{k=1}^n d_n \mathopen{}\left( \frac 1 k \right)\mathclose{}$.
You are given:

$S(7) = 0 + 0 + 3 + 0 + 0 + 6 + 1 = 10$
$S(100) = 418$

Find $S(10^7)$.


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
