#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 429
# https://projecteuler.net/problem=429
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
solution to Project Euler problem 429
https://projecteuler.net/problem=429

A unitary divisor $d$ of a number $n$ is a divisor of $n$ that has the property $\gcd(d, n/d) = 1$.

The unitary divisors of $4! = 24$ are $1, 3, 8$ and $24$.

The sum of their squares is $1^2 + 3^2 + 8^2 + 24^2 = 650$.


Let $S(n)$ represent the sum of the squares of the unitary divisors of $n$. Thus $S(4!)=650$.


Find $S(100\,000\,000!)$ modulo $1\,000\,000\,009$.


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