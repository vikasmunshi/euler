#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 188
# https://projecteuler.net/problem=188
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
solution to Project Euler problem 188
https://projecteuler.net/problem=188
The hyperexponentiation or tetration of a number $a$ by a positive integer $b$, denoted by $a\mathbin{\uparrow \uparrow}b$ or $^b a$, is recursively defined by:


$a \mathbin{\uparrow \uparrow} 1 = a$,

$a \mathbin{\uparrow \uparrow} (k+1) = a^{(a \mathbin{\uparrow \uparrow} k)}$.

Thus we have e.g. $3 \mathbin{\uparrow \uparrow} 2 = 3^3 = 27$, hence $3 \mathbin{\uparrow \uparrow} 3 = 3^{27} = 7625597484987$ and $3 \mathbin{\uparrow \uparrow} 4$ is roughly $10^{3.6383346400240996 \cdot 10^{12}}$.
Find the last $8$ digits of $1777 \mathbin{\uparrow \uparrow} 1855$.

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