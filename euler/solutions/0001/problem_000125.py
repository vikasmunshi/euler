#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 125
# https://projecteuler.net/problem=125
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
solution to Project Euler problem 125
https://projecteuler.net/problem=125
The palindromic number $595$ is interesting because it can be written as the sum of consecutive squares: $6^2 + 7^2 + 8^2 + 9^2 + 10^2 + 11^2 + 12^2$.
There are exactly eleven palindromes below one-thousand that can be written as consecutive square sums, and the sum of these palindromes is $4164$. Note that $1 = 0^2 + 1^2$ has not been included as this problem is concerned with the squares of positive integers.
Find the sum of all the numbers less than $10^8$ that are both palindromic and can be written as the sum of consecutive squares.


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