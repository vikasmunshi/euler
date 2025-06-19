#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 930
# https://projecteuler.net/problem=930
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
solution to Project Euler problem 930
https://projecteuler.net/problem=930
Given $n\ge 2$ bowls arranged in a circle, $m\ge 2$ balls are distributed amongst them.

Initially the balls are distributed randomly: for each ball, a bowl is chosen equiprobably and independently of the other balls. After this is done, we start the following process:

Choose one of the $m$ balls equiprobably at random.
Choose a direction to move - either clockwise or anticlockwise - again equiprobably at random.
Move the chosen ball to the neighbouring bowl in the chosen direction.
Return to step 1.


This process stops when all the $m$ balls are located in the same bowl. Note that this may be after zero steps, if the balls happen to have been initially distributed all in the same bowl.

Let $F(n, m)$ be the expected number of times we move a ball before the process stops. For example, $F(2, 2) = \frac{1}{2}$, $F(3, 2) = \frac{4}{3}$, $F(2, 3) = \frac{9}{4}$, and $F(4, 5) = \frac{6875}{24}$.

Let $G(N, M) = \sum_{n=2}^N \sum_{m=2}^M F(n, m)$. For example, $G(3, 3) = \frac{137}{12}$ and $G(4, 5) = \frac{6277}{12}$. You are also given that $G(6, 6) \approx 1.681521567954e4$ in scientific format with 12 significant digits after the decimal point.

Find $G(12, 12)$. Give your answer in scientific format with 12 significant digits after the decimal point.


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