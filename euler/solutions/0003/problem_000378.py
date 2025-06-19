#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 378
# https://projecteuler.net/problem=378
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
solution to Project Euler problem 378
https://projecteuler.net/problem=378
Let $T(n)$ be the nth triangle number, so $T(n) = \dfrac{n(n + 1)}{2}$.

Let $dT(n)$ be the number of divisors of $T(n)$.

E.g.: $T(7) = 28$ and $dT(7) = 6$.

Let $Tr(n)$ be the number of triples $(i, j, k)$ such that $1 \le i \lt j \lt k \le n$ and $dT(i) \gt dT(j) \gt dT(k)$.

$Tr(20) = 14$, $Tr(100) = 5772$, and $Tr(1000) = 11174776$.

Find $Tr(60 000 000)$. 

Give the last 18 digits of your answer.


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