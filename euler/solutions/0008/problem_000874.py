#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 874
# https://projecteuler.net/problem=874
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
solution to Project Euler problem 874
https://projecteuler.net/problem=874

Let $p(t)$ denote the $(t+1)$th prime number. So that $p(0) = 2$, $p(1) = 3$, etc.

We define the prime score of a list of nonnegative integers $[a_1, ..., a_n]$ as the sum $\sum_{i = 1}^n p(a_i)$.

Let $M(k, n)$ be the maximal prime score among all lists $[a_1, ..., a_n]$ such that:


 $0 \leq a_i  the sum $\sum_{i = 1}^n a_i$ is a multiple of $k$.



For example, $M(2, 5) = 14$ as $[0, 1, 1, 1, 1]$ attains a maximal prime score of $14$.


Find $M(7000, p(7000))$.

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