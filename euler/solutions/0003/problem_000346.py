#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 346
# https://projecteuler.net/problem=346
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
solution to Project Euler problem 346
https://projecteuler.net/problem=346

The number $7$ is special, because $7$ is $111$ written in base $2$, and $11$ written in base $6$ (i.e. $7_{10} = 11_6 = 111_2$). In other words, $7$ is a repunit in at least two bases $b \gt 1$. 


We shall call a positive integer with this property a strong repunit. It can be verified that there are $8$ strong repunits below $50$: $\{1,7,13,15,21,31,40,43\}$.

Furthermore, the sum of all strong repunits below $1000$ equals $15864$.

Find the sum of all strong repunits below $10^{12}$.




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