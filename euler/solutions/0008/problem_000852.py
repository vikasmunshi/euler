#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 852
# https://projecteuler.net/problem=852
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
solution to Project Euler problem 852
https://projecteuler.net/problem=852
This game has a box of $N$ unfair coins and $N$ fair coins. Fair coins have probability 50% of landing heads while unfair coins have probability 75% of landing heads.

The player begins with a score of 0 which may become negative during play.

At each round the player randomly picks a coin from the box and guesses its type: fair or unfair. Before guessing they may toss the coin any number of times; however, each toss subtracts 1 from their score. The decision to stop tossing and make a guess can be made at any time. After guessing the player's score is increased by 20 if they are right and decreased by 50 if they are wrong. Then the coin type is revealed to the player and the coin is discarded.

After $2N$ rounds the box will be empty and the game is over. Let $S(N)$ be the expected score of the player at the end of the game assuming that they play optimally in order to maximize their expected score.

You are given $S(1) = 20.558591$ rounded to 6 digits after the decimal point.

Find $S(50)$. Give your answer rounded to 6 digits after the decimal point.

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