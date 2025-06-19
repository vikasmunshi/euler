#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 888
# https://projecteuler.net/problem=888
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
solution to Project Euler problem 888
https://projecteuler.net/problem=888

Two players play a game with a number of piles of stones, alternating turns. Each turn a player can choose to remove 1, 2, 4, or 9 stones from a single pile; or alternatively they can choose to split a pile containing two or more stones into two non-empty piles. The winner is the player who removes the last stone.


A collection of piles is called a losing position if the player to move cannot force a win with optimal play. Define $S(N, m)$ to be the number of distinct losing positions arising from $m$ piles of stones where each pile contains from $1$ to $N$ stones. Two positions are considered equivalent if they consist of the same pile sizes. That is, the order of the piles does not matter.


You are given $S(12,4)=204$ and $S(124,9)=2259208528408$.


Find $S(12491249,1249)$. Give your answer modulo $912491249$.


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