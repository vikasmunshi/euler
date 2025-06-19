#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 571
# https://projecteuler.net/problem=571
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
solution to Project Euler problem 571
https://projecteuler.net/problem=571
A positive number is pandigital in base $b$ if it contains all digits from $0$ to $b - 1$ at least once when written in base $b$.

An $n$-super-pandigital number is a number that is simultaneously pandigital in all bases from $2$ to $n$ inclusively.

For example $978 = 1111010010_2 = 1100020_3 = 33102_4 = 12403_5$ is the smallest $5$-super-pandigital number.

Similarly, $1093265784$ is the smallest $10$-super-pandigital number.

The sum of the $10$ smallest $10$-super-pandigital numbers is $20319792309$.

What is the sum of the $10$ smallest $12$-super-pandigital numbers?

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