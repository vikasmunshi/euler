#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 848
# https://projecteuler.net/problem=848
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
solution to Project Euler problem 848
https://projecteuler.net/problem=848
Two players play a game. At the start of the game each player secretly chooses an integer; the first player from $1,...,n$ and the second player from $1,...,m$. Then they take alternate turns, starting with the first player. The player, whose turn it is, displays a set of numbers and the other player tells whether their secret number is in the set or not. The player to correctly guess a set with a single number is the winner and the game ends.

Let $p(m,n)$ be the winning probability of the first player assuming both players play optimally. For example $p(1, n) = 1$ and $p(m, 1) = 1/m$.

You are also given $p(7,5) \approx 0.51428571$.

Find $\displaystyle \sum_{i=0}^{20}\sum_{j=0}^{20} p(7^i, 5^j)$ and give your answer rounded to 8 digits after the decimal point.

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