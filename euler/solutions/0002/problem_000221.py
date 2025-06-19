#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 221
# https://projecteuler.net/problem=221
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
solution to Project Euler problem 221
https://projecteuler.net/problem=221
We shall call a positive integer $A$ an "Alexandrian integer", if there exist integers $p, q, r$ such that:

$$A = p \cdot q \cdot r$$
and
$$\dfrac{1}{A} = \dfrac{1}{p} + \dfrac{1}{q} + \dfrac{1}{r}.$$

For example, $630$ is an Alexandrian integer ($p = 5, q = -7, r = -18$).
In fact, $630$ is the $6$th Alexandrian integer,  the first $6$ Alexandrian integers being: $6, 42, 120, 156, 420$, and $630$.

Find the $150000$th Alexandrian integer.

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