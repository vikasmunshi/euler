#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 856
# https://projecteuler.net/problem=856
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
solution to Project Euler problem 856
https://projecteuler.net/problem=856
A standard 52-card deck comprises 13 ranks in four suits. A pair is a set of two cards of the same rank.

Cards are drawn, without replacement, from a well shuffled 52-card deck waiting for consecutive cards that form a pair. For example, the probability of finding a pair in the first two draws is $\frac{1}{17}$.

Cards are drawn until either such a pair is found or the pack is exhausted waiting for one. In the latter case we say that all 52 cards were drawn.

Find the expected number of cards that were drawn. Give your answer rounded to eight places after the decimal point.

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