#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 537
# https://projecteuler.net/problem=537
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
solution to Project Euler problem 537
https://projecteuler.net/problem=537

Let $\pi(x)$ be the prime counting function, i.e. the number of prime numbers less than or equal to $x$.

For example,$\pi(1)=0$, $\pi(2)=1$, $\pi(100)=25$.


Let $T(n, k)$ be the number of $k$-tuples $(x_1, ..., x_k)$ which satisfy:

1. every $x_i$ is a positive integer;

2. $\displaystyle \sum_{i=1}^k \pi(x_i)=n$


For example $T(3,3)=19$.

The $19$ tuples are $(1,1,5)$, $(1,5,1)$, $(5,1,1)$, $(1,1,6)$, $(1,6,1)$, $(6,1,1)$, $(1,2,3)$, $(1,3,2)$, $(2,1,3)$, $(2,3,1)$, $(3,1,2)$, $(3,2,1)$, $(1,2,4)$, $(1,4,2)$, $(2,1,4)$, $(2,4,1)$, $(4,1,2)$, $(4,2,1)$, $(2,2,2)$.


You are given $T(10, 10) = 869\,985$ and $T(10^3,10^3) \equiv 578\,270\,566 \pmod{1\,004\,535\,809}$.

Find $T(20\,000, 20\,000) \pmod{1\,004\,535\,809}$.





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