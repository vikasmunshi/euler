#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 611
# https://projecteuler.net/problem=611
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
solution to Project Euler problem 611
https://projecteuler.net/problem=611
Peter moves in a hallway with $N + 1$ doors consecutively numbered from $0$ through $N$. All doors are initially closed. Peter starts in front of door $0$, and repeatedly performs the following steps:
First, he walks a positive square number of doors away from his position.
Then he walks another, larger square number of doors away from his new position.
He toggles the door he faces (opens it if closed, closes it if open).
And finally returns to door $0$.
We call an action any sequence of those steps. Peter never performs the exact same action twice, and makes sure to perform all possible actions that don't bring him past the last door.
Let $F(N)$ be the number of doors that are open after Peter has performed all possible actions. You are given that $F(5) = 1$, $F(100) = 27$, $F(1000) = 233$ and $F(10^6) = 112168$.
Find $F(10^{12})$.

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