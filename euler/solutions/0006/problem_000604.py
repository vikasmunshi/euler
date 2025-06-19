#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 604
# https://projecteuler.net/problem=604
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
solution to Project Euler problem 604
https://projecteuler.net/problem=604

Let $F(N)$ be the maximum number of lattice points in an axis-aligned $N\times N$ square that the graph of a single strictly convex increasing function can pass through.


You are given that $F(1) = 2$, $F(3) = 3$,  $F(9) = 6$, $F(11) = 7$, $F(100) = 30$ and $F(50000) = 1898$.
 
Below is the graph of a function reaching the maximum $3$ for $N=3$:




Find $F(10^{18})$.



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