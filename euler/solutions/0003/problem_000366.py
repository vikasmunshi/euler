#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 366
# https://projecteuler.net/problem=366
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
solution to Project Euler problem 366
https://projecteuler.net/problem=366

Two players, Anton and Bernhard, are playing the following game.

There is one pile of $n$ stones.

The first player may remove any positive number of stones, but not the whole pile.

Thereafter, each player may remove at most twice the number of stones his opponent took on the previous move.

The player who removes the last stone wins.


E.g. $n=5$.

If the first player takes anything more than one stone the next player will be able to take all remaining stones.

If the first player takes one stone, leaving four, his opponent will take also one stone, leaving three stones.

The first player cannot take all three because he may take at most $2 \times 1=2$ stones. So let's say he takes also one stone, leaving $2$. The second player can take the two remaining stones and wins.

So $5$ is a losing position for the first player.

For some winning positions there is more than one possible move for the first player.

E.g. when $n=17$ the first player can remove one or four stones.


Let $M(n)$ be the maximum number of stones the first player can take from a winning position at his first turn and $M(n)=0$ for any other position.


$\sum M(n)$ for $n \le 100$ is $728$.


Find $\sum M(n)$ for $n \le 10^{18}$.
Give your answer modulo $10^8$.


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