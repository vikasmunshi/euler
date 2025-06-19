#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 400
# https://projecteuler.net/problem=400
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
solution to Project Euler problem 400
https://projecteuler.net/problem=400

A Fibonacci tree is a binary tree recursively defined as:$T(0)$ is the empty tree.
$T(1)$ is the binary tree with only one node.
$T(k)$ consists of a root node that has $T(k-1)$ and $T(k-2)$ as children.

On such a tree two players play a take-away game. On each turn a player selects a node and removes that node along with the subtree rooted at that node.

The player who is forced to take the root node of the entire tree loses.


Here are the winning moves of the first player on the first turn for $T(k)$ from $k=1$ to $k=6$.




Let $f(k)$ be the number of winning moves of the first player (i.e. the moves for which the second player has no winning strategy) on the first turn of the game when this game is played on $T(k)$.



For example, $f(5) = 1$ and $f(10) = 17$.



Find $f(10000)$. Give the last $18$ digits of your answer.


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