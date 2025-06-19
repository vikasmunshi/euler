#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 870
# https://projecteuler.net/problem=870
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
solution to Project Euler problem 870
https://projecteuler.net/problem=870

Two players play a game with a single pile of stones of initial size $n$. They take stones from the pile in turn, according to the following rules which depend on a fixed real number $r > 0$:



In the first turn, the first player may take $k$ stones with $1 \le k \lt n$.

If a player takes $m$ stones in a turn, then in the next turn the opponent may take $k$ stones with $1 \le k \le \lfloor r \cdot m \rfloor$.


Whoever cannot make a legal move loses the game.


Let $L(r)$ be the set of initial pile sizes $n$ for which the second player has a winning strategy. For example, $L(0.5) = \{1\}$, $L(1) = \{1, 2, 4, 8, 16, ...\}$, $L(2) = \{1, 2, 3, 5, 8, ...\}$.


A real number $q \gt 0$ is a transition value if $L(s)$ is different from $L(t)$ for all $s < q < t$.

Let $T(i)$ be the $i$-th transition value. For example, $T(1) = 1$, $T(2) = 2$, $T(22) \approx 6.3043478261$.


Find $T(123456)$ and give your answer rounded to $10$ digits after the decimal point.

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