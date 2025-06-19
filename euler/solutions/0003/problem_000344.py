#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 344
# https://projecteuler.net/problem=344
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
solution to Project Euler problem 344
https://projecteuler.net/problem=344
One variant of N.G. de Bruijn's silver dollar game can be described as follows:

On a strip of squares a number of coins are placed, at most one coin per square. Only one coin, called the silver dollar, has any value. Two players take turns making moves. At each turn a player must make either a regular or a special move.

A regular move consists of selecting one coin and moving it one or more squares to the left. The coin cannot move out of the strip or jump on or over another coin.

Alternatively, the player can choose to make the special move of pocketing the leftmost coin rather than making a regular move. If no regular moves are possible, the player is forced to pocket the leftmost coin.

The winner is the player who pockets the silver dollar.






A winning configuration is an arrangement of coins on the strip where the first player can force a win no matter what the second player does.

Let $W(n,c)$ be the number of winning configurations for a strip of $n$ squares, $c$ worthless coins and one silver dollar.

You are given that $W(10,2) = 324$ and $W(100,10) = 1514704946113500$.

Find $W(1\,000\,000, 100)$ modulo the semiprime $1000\,036\,000\,099$ ($= 1\,000\,003 \cdot 1\,000\,033$).



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