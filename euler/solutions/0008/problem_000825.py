#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 825
# https://projecteuler.net/problem=825
# Answer: 
# Notes: 
import textwrap
from typing import Any, Dict

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol, SolutionResult

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=None, ),
]


def solution(**kwarg: Dict[str, Any]) -> SolutionResult:
    # enter the solution here
    raise NotImplementedError


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 825
https://projecteuler.net/problem=825
Two cars are on a circular track of total length $2n$, facing the same direction, initially distance $n$ apart.

They move in turn. At each turn, the moving car will advance a distance of $1$, $2$ or $3$, with equal probabilities.

The chase ends when the moving car reaches or goes beyond the position of the other car. The moving car is declared the winner.

Let $S(n)$ be the difference between the winning probabilities of the two cars.

For example, when $n = 2$, the winning probabilities of the two cars are $\frac 9 {11}$ and $\frac 2 {11}$, and thus $S(2) = \frac 7 {11}$.

Let $\displaystyle T(N) = \sum_{n = 2}^N S(n)$.

You are given that $T(10) = 2.38235282$ rounded to 8 digits after the decimal point.

Find $T(10^{14})$, rounded to 8 digits after the decimal point.

''').strip()

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
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)