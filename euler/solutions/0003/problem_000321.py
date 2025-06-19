#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 321
# https://projecteuler.net/problem=321
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
solution to Project Euler problem 321
https://projecteuler.net/problem=321
A horizontal row comprising of $2n + 1$ squares has $n$ red counters placed at one end and $n$ blue counters at the other end, being separated by a single empty square in the centre. For example, when $n = 3$.



A counter can move from one square to the next (slide) or can jump over another counter (hop) as long as the square next to that counter is unoccupied.



Let $M(n)$ represent the minimum number of moves/actions to completely reverse the positions of the coloured counters; that is, move all the red counters to the right and all the blue counters to the left.
It can be verified $M(3) = 15$, which also happens to be a triangle number.

If we create a sequence based on the values of $n$ for which $M(n)$ is a triangle number then the first five terms would be:

$1$, $3$, $10$, $22$, and $63$, and their sum would be $99$.

Find the sum of the first forty terms of this sequence.

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