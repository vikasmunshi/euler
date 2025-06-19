#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 686
# https://projecteuler.net/problem=686
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
solution to Project Euler problem 686
https://projecteuler.net/problem=686
$2^7=128$ is the first power of two whose leading digits are "12".

The next power of two whose leading digits are "12" is $2^{80}$.

Define $p(L, n)$ to be the $n$th-smallest value of $j$ such that the base 10 representation of $2^j$ begins with the digits of $L$.

So $p(12, 1) = 7$ and $p(12, 2) = 80$.

You are also given that $p(123, 45) = 12710$.

Find $p(123, 678910)$.


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