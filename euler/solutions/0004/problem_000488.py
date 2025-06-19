#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 488
# https://projecteuler.net/problem=488
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
solution to Project Euler problem 488
https://projecteuler.net/problem=488
Alice and Bob have enjoyed playing Nim every day. However, they finally got bored of playing ordinary three-heap Nim.

So, they added an extra rule:

- Must not make two heaps of the same size.

The triple $(a, b, c)$ indicates the size of three heaps.

Under this extra rule, $(2,4,5)$ is one of the losing positions for the next player.

To illustrate:

- Alice moves to $(2,4,3)$

- Bob   moves to $(0,4,3)$

- Alice moves to $(0,2,3)$

- Bob   moves to $(0,2,1)$

Unlike ordinary three-heap Nim, $(0,1,2)$ and its permutations are the end states of this game.

For an integer $N$, we define $F(N)$ as the sum of $a + b + c$ for all the losing positions for the next player, with $0 \lt a \lt b \lt c \lt N$.

For example, $F(8) = 42$, because there are $4$ losing positions for the next player, $(1,3,5)$, $(1,4,6)$, $(2,3,6)$ and $(2,4,5)$.

We can also verify that $F(128) = 496062$.

Find the last $9$ digits of $F(10^{18})$.

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