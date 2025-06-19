#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 129
# https://projecteuler.net/problem=129
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
solution to Project Euler problem 129
https://projecteuler.net/problem=129
A number consisting entirely of ones is called a repunit. We shall define $R(k)$ to be a repunit of length $k$; for example, $R(6) = 111111$.
Given that $n$ is a positive integer and $\gcd(n, 10) = 1$, it can be shown that there always exists a value, $k$, for which $R(k)$ is divisible by $n$, and let $A(n)$ be the least such value of $k$; for example, $A(7) = 6$ and $A(41) = 5$.
The least value of $n$ for which $A(n)$ first exceeds ten is $17$.
Find the least value of $n$ for which $A(n)$ first exceeds one-million.


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