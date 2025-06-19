#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 128
# https://projecteuler.net/problem=128
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
solution to Project Euler problem 128
https://projecteuler.net/problem=128
A hexagonal tile with number $1$ is surrounded by a ring of six hexagonal tiles, starting at "12 o'clock" and numbering the tiles $2$ to $7$ in an anti-clockwise direction.
New rings are added in the same fashion, with the next rings being numbered $8$ to $19$, $20$ to $37$, $38$ to $61$, and so on. The diagram below shows the first three rings.


By finding the difference between tile $n$ and each of its six neighbours we shall define $\operatorname{PD}(n)$ to be the number of those differences which are prime.
For example, working clockwise around tile $8$ the differences are $12, 29, 11, 6, 1$, and $13$. So $\operatorname{PD}(8) = 3$.
In the same way, the differences around tile $17$ are $1, 17, 16, 1, 11$, and $10$, hence $\operatorname{PD}(17) = 2$.
It can be shown that the maximum value of $\operatorname{PD}(n)$ is $3$.
If all of the tiles for which $\operatorname{PD}(n) = 3$ are listed in ascending order to form a sequence, the $10$th tile would be $271$.
Find the $2000$th tile in this sequence.


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