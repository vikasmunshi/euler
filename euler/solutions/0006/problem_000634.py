#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 634
# https://projecteuler.net/problem=634
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
solution to Project Euler problem 634
https://projecteuler.net/problem=634

Define $F(n)$ to be the number of integers $x≤n$ that can be written in the form $x=a^2b^3$, where $a$ and $b$ are integers not necessarily different and both greater than 1.

For example, $32=2^2\times 2^3$  and $72=3^2\times 2^3$ are the only two integers less than $100$ that can be written in this form. Hence, $F(100)=2$.


Further you are given $F(2\times 10^4)=130$ and $F(3\times 10^6)=2014$.


Find $F(9\times 10^{18})$.


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