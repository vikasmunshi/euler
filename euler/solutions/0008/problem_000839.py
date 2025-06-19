#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 839
# https://projecteuler.net/problem=839
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
solution to Project Euler problem 839
https://projecteuler.net/problem=839

The sequence $S_n$ is defined by $S_0 = 290797$ and $S_n = S_{n - 1}^2 \bmod 50515093$ for $n > 0$.

There are $N$ bowls indexed $0,1,... ,N-1$. Initially there are $S_n$ beans in bowl $n$.


At each step, the smallest index $n$ is found such that bowl $n$ has strictly more beans than bowl $n+1$. Then one bean is moved from bowl $n$ to bowl $n+1$.


Let $B(N)$ be the number of steps needed to sort the bowls into non-descending order.

For example, $B(5) = 0$, $B(6) = 14263289$ and $B(100)=3284417556$.


Find $B(10^7)$.

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