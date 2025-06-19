#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 104
# https://projecteuler.net/problem=104
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
solution to Project Euler problem 104
https://projecteuler.net/problem=104
The Fibonacci sequence is defined by the recurrence relation:
$F_n = F_{n - 1} + F_{n - 2}$, where $F_1 = 1$ and $F_2 = 1$.
It turns out that $F_{541}$, which contains $113$ digits, is the first Fibonacci number for which the last nine digits are $1$-$9$ pandigital (contain all the digits $1$ to $9$, but not necessarily in order). And $F_{2749}$, which contains $575$ digits, is the first Fibonacci number for which the first nine digits are $1$-$9$ pandigital.
Given that $F_k$ is the first Fibonacci number for which the first nine digits AND the last nine digits are $1$-$9$ pandigital, find $k$.


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