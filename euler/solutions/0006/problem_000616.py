#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 616
# https://projecteuler.net/problem=616
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
solution to Project Euler problem 616
https://projecteuler.net/problem=616
Alice plays the following game, she starts with a list of integers $L$ and on each step she can either:
remove two elements $a$ and $b$ from $L$ and add $a^b$ to $L$
or conversely remove an element $c$ from $L$ that can be written as $a^b$, with $a$ and $b$ being two integers such that $a, b > 1$, and add both $a$ and $b$ to $L$ 
For example starting from the list $L=\{8\}$, Alice can remove $8$ and add $2$ and $3$ resulting in $L=\{2,3\}$ in a first step. Then she can obtain $L=\{9\}$ in a second step.

Note that the same integer is allowed to appear multiple times in the list.

An integer $n>1$ is said to be creative if for any integer $m \gt 1$ Alice can obtain a list that contains $m$ starting from $L=\{n\}$.

Find the sum of all creative integers less than or equal to $10^{12}$.

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