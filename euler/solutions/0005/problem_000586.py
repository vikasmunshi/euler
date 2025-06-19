#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 586
# https://projecteuler.net/problem=586
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
solution to Project Euler problem 586
https://projecteuler.net/problem=586

The number $209$ can be expressed as $a^2 + 3ab + b^2$ in two distinct ways:


$ \qquad 209 = 8^2 + 3\cdot 8\cdot 5 + 5^2$ 

$ \qquad 209 = 13^2 + 3\cdot13\cdot 1 + 1^2$


Let $f(n,r)$ be the number of integers $k$ not exceeding $n$ that can be expressed as $k=a^2 + 3ab + b^2$, with $a \gt b \gt 0$ integers, in exactly $r$ different ways.


You are given that $f(10^5, 4) = 237$ and $f(10^8, 6) = 59517$.


Find $f(10^{15}, 40)$.


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