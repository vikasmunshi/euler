#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 746
# https://projecteuler.net/problem=746
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
solution to Project Euler problem 746
https://projecteuler.net/problem=746
$n$ families, each with four members, a father, a mother, a son and a daughter, were invited to a restaurant. They were all seated at a large circular table with $4n$ seats such that men and women alternate.

Let $M(n)$ be the number of ways the families can be seated such that none of the families were seated together. A family is considered to be seated together only when all the members of a family sit next to each other.

For example, $M(1)=0$, $M(2)=896$, $M(3)=890880$ and $M(10) \equiv 170717180 \pmod {1\,000\,000\,007}$.

Let $S(n)=\displaystyle \sum_{k=2}^nM(k)$.

For example, $S(10) \equiv 399291975 \pmod {1\,000\,000\,007}$.

Find $S(2021)$. Give your answer modulo $1\,000\,000\,007$.


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