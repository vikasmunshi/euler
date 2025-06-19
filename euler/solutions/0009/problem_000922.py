#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 922
# https://projecteuler.net/problem=922
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
solution to Project Euler problem 922
https://projecteuler.net/problem=922

A Young diagram is a finite collection of (equally-sized) squares in a grid-like arrangement of rows and columns, such that

the left-most squares of all rows are aligned vertically;
the top squares of all columns are aligned horizontally;
the rows are non-increasing in size as we move top to bottom;
the columns are non-increasing in size as we move left to right.


Two examples of Young diagrams are shown below.



Two players Right and Down play a game on several Young diagrams, all disconnected from each other. Initially, a token is placed in the top-left square of each diagram. Then they take alternating turns, starting with Right. On Right's turn, Right selects a token on one diagram and moves it any number of squares to the right. On Down's turn, Down selects a token on one diagram and moves it any number of squares downwards. A player unable to make a legal move on their turn loses the game.


For $a,b,k\geq 1$ we define an $(a,b,k)$-staircase to be the Young diagram where the bottom-right frontier consists of $k$ steps of vertical height $a$ and horizontal length $b$. Shown below are four examples of staircases with $(a,b,k)$ respectively $(1,1,4),$ $(5,1,1),$ $(3,3,2),$ $(2,4,3)$.



Additionally, define the weight of an $(a,b,k)$-staircase to be $a+b+k$.


Let $R(m, w)$ be the number ways of choosing $m$ staircases, each having weight not exceeding $w$, upon which Right (moving first in the game) will win the game assuming optimal play. Different orderings of the same set of staircases are to be counted separately.


For example, $R(2, 4)=7$ is illustrated below, with tokens as grey circles drawn in their initial positions.




You are also given $R(3, 9)=314104$.


Find $R(8, 64)$ giving your answer modulo $10^9+7$.

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