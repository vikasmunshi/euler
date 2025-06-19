#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 474
# https://projecteuler.net/problem=474
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
solution to Project Euler problem 474
https://projecteuler.net/problem=474

For a positive integer $n$ and digits $d$, we define $F(n, d)$ as the number of the divisors of $n$ whose last digits equal $d$.

For example, $F(84, 4) = 3$. Among the divisors of $84$ ($1, 2, 3, 4, 6, 7, 12, 14, 21, 28, 42, 84$), three of them ($4, 14, 84$) have the last digit $4$.


We can also verify that $F(12!, 12) = 11$ and $F(50!, 123) = 17888$.


Find $F(10^6!, 65432)$ modulo ($10^{16} + 61$).


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