#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 926
# https://projecteuler.net/problem=926
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
solution to Project Euler problem 926
https://projecteuler.net/problem=926

A round number is a number that ends with one or more zeros in a given base.


Let us define the roundness of a number $n$ in base $b$ as the number of zeros at the end of the base $b$ representation of $n$.

For example, $20$ has roundness $2$ in base $2$, because the base $2$ representation of $20$ is $10100$, which ends with $2$ zeros.


Also define $R(n)$, the total roundness of a number $n$, as the sum of the roundness of $n$ in base $b$ for all $b > 1$.

For example, $20$ has roundness $2$ in base $2$ and roundness $1$ in base $4$, $5$, $10$, $20$, hence we get $R(20)=6$.

You are also given $R(10!) = 312$.


Find $R(10\,000\,000!)$. Give your answer modulo $10^9 + 7$.

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