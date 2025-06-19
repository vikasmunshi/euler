#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 254
# https://projecteuler.net/problem=254
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
solution to Project Euler problem 254
https://projecteuler.net/problem=254
Define $f(n)$ as the sum of the factorials of the digits of $n$. For example, $f(342) = 3! + 4! + 2! = 32$.

Define $sf(n)$ as the sum of the digits of $f(n)$. So $sf(342) = 3 + 2 = 5$.

Define $g(i)$ to be the smallest positive integer $n$ such that $sf(n) = i$. Though $sf(342)$ is $5$, $sf(25)$ is also $5$, and it can be verified that $g(5)$ is $25$.

Define $sg(i)$ as the sum of the digits of $g(i)$. So $sg(5) = 2 + 5 = 7$.

Further, it can be verified that $g(20)$ is $267$ and $\sum sg(i)$ for $1 \le i \le 20$ is $156$.

What is $\sum sg(i)$ for $1 \le i \le 150$?

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