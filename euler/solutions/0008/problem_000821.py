#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 821
# https://projecteuler.net/problem=821
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
solution to Project Euler problem 821
https://projecteuler.net/problem=821

A set, $S$, of integers is called 123-separable if $S$, $2S$ and $3S$ are disjoint. Here $2S$ and $3S$ are obtained by multiplying all the elements in $S$ by $2$ and $3$ respectively.


Define $F(n)$ to be the maximum number of elements of
$$(S\cup 2S \cup 3S)\cap \{1,2,3,\ldots,n\}$$
where $S$ ranges over all 123-separable sets.


For example, $F(6) = 5$ can be achieved with either $S = \{1,4,5\}$ or $S = \{1,5,6\}$.

You are also given $F(20) = 19$.


Find $F(10^{16})$.

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