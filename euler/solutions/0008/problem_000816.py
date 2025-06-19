#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 816
# https://projecteuler.net/problem=816
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
solution to Project Euler problem 816
https://projecteuler.net/problem=816
We create an array of points  $P_n$ in a two dimensional plane using the following random number generator:

$s_0=290797$

$s_{n+1}={s_n}^2 \bmod 50515093$

 

$P_n=(s_{2n},s_{2n+1})$

Let $d(k)$  be the shortest distance of any two (distinct) points among $P_0, \cdots, P_{k - 1}$.

E.g. $d(14)=546446.466846479$.


Find $d(2000000)$. Give your answer rounded to $9$ places after the decimal point.


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