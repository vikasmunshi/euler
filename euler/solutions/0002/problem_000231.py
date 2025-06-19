#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 231
# https://projecteuler.net/problem=231
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
solution to Project Euler problem 231
https://projecteuler.net/problem=231
The binomial coefficient $\displaystyle \binom {10} 3 = 120$.

$120 = 2^3 \times 3 \times 5 = 2 \times 2 \times 2 \times 3 \times 5$, and $2 + 2 + 2 + 3 + 5 = 14$.

So the sum of the terms in the prime factorisation of $\displaystyle \binom {10} 3$ is $14$.



Find the sum of the terms in the prime factorisation of $\displaystyle \binom {20\,000\,000} {15\,000\,000}$.


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