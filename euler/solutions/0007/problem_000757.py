#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 757
# https://projecteuler.net/problem=757
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
solution to Project Euler problem 757
https://projecteuler.net/problem=757

A positive integer $N$ is stealthy, if there exist positive integers $a$, $b$, $c$, $d$ such that $ab = cd = N$ and $a+b = c+d+1$.

For example, $36 = 4\times 9 = 6\times 6$ is stealthy.


You are also given that there are 2851 stealthy numbers not exceeding $10^6$.


How many stealthy numbers  are there that don't exceed $10^{14}$?


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