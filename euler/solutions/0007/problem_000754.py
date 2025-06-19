#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 754
# https://projecteuler.net/problem=754
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
solution to Project Euler problem 754
https://projecteuler.net/problem=754
The Gauss Factorial of a number $n$ is defined as the product of all positive numbers $\leq n$ that are relatively prime to $n$. For example $g(10)=1\times 3\times 7\times 9 = 189$. 
Also we define
$$\displaystyle G(n) = \prod_{i=1}^{n}g(i)$$
You are given $G(10) = 23044331520000$.

Find $G(10^8)$. Give your answer modulo $1\,000\,000\,007$.

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