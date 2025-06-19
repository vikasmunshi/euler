#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 882
# https://projecteuler.net/problem=882
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
solution to Project Euler problem 882
https://projecteuler.net/problem=882
Dr. One and Dr. Zero are playing the following partisan game.

The game begins with one $1$, two $2$'s, three $3$'s, ..., $n$ $n$'s. Starting with Dr. One, they make moves in turn.

Dr. One chooses a number and changes it by removing a $1$ from its binary expansion.

Dr. Zero chooses a number and changes it by removing a $0$ from its binary expansion.

The player that is unable to move loses.

Note that leading zeros are not allowed in any binary expansion; in particular nobody can make a move on the number $0$.

They soon realize that Dr. Zero can never win the game. In order to make it more interesting, Dr. Zero is allowed to "skip the turn" several times, i.e. passing the turn back to Dr. One without making a move.

For example, when $n = 2$, Dr. Zero can win the game if allowed to skip $2$ turns. A sample game:
$$
[1, 2, 2]\xrightarrow{\textrm{Dr. One}}[1, 0, 2]\xrightarrow{\textrm{Dr. Zero}}[1, 0, 1]\xrightarrow{\textrm{Dr. One}}[1, 0, 0]\xrightarrow[\textrm{skip}]{\textrm{Dr. Zero}}
[1, 0, 0]\xrightarrow{\textrm{Dr. One}}[0, 0, 0]\xrightarrow[\textrm{skip}]{\textrm{Dr. Zero}}[0, 0, 0].
$$
Let $S(n)$ be the minimal number of skips needed so that Dr. Zero has a winning strategy.

For example, $S(2) = 2$, $S(5) = 17$, $S(10) = 64$.

Find $S(10^5)$.

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