#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 436
# https://projecteuler.net/problem=436
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
solution to Project Euler problem 436
https://projecteuler.net/problem=436
Julie proposes the following wager to her sister Louise.

She suggests they play a game of chance to determine who will wash the dishes.

For this game, they shall use a generator of independent random numbers uniformly distributed between $0$ and $1$.

The game starts with $S = 0$.

The first player, Louise, adds to $S$ different random numbers from the generator until $S \gt 1$ and records her last random number '$x$'.

The second player, Julie, continues adding to $S$ different random numbers from the generator until $S \gt 2$ and records her last random number '$y$'.

The player with the highest number wins and the loser washes the dishes, i.e. if $y \gt x$ the second player wins.

For example, if the first player draws $0.62$ and $0.44$, the first player turn ends since $0.62+0.44 \gt 1$ and $x = 0.44$.

If the second players draws $0.1$, $0.27$ and $0.91$, the second player turn ends since $0.62+0.44+0.1+0.27+0.91 \gt 2$ and $y = 0.91$.
Since $y \gt x$, the second player wins.

Louise thinks about it for a second, and objects: "That's not fair".

What is the probability that the second player wins?

Give your answer rounded to $10$ places behind the decimal point in the form 0.abcdefghij.


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