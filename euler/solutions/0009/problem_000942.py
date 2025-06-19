#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 942
# https://projecteuler.net/problem=942
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
solution to Project Euler problem 942
https://projecteuler.net/problem=942
Given a natural number $q$, let $p = 2^q - 1$ be the $q$-th Mersenne number.

Let $R(q)$ be the minimal square root of $q$ modulo $p$, if one exists. In other words, $R(q)$ is the smallest positive integer $x$ such that $x^2 - q$ is divisible by $p$.

For example, $R(5)=6$ and $R(17)=47569$.

Find $R(74\,207\,281)$. Give your answer modulo $10^9 + 7$.

Note: $2^{74207281}-1$ is prime.

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