#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 535
# https://projecteuler.net/problem=535
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
solution to Project Euler problem 535
https://projecteuler.net/problem=535
Consider the infinite integer sequence S starting with:

$S = 1, 1, 2, 1, 3, 2, 4, 1, 5, 3, 6, 2, 7, 8, 4, 9, 1, 10, 11, 5, ...$

Circle the first occurrence of each integer.

$S = \enclose{circle}1, 1, \enclose{circle}2, 1, \enclose{circle}3, 2, \enclose{circle}4, 1, \enclose{circle}5, 3, \enclose{circle}6, 2, \enclose{circle}7, \enclose{circle}8, 4, \enclose{circle}9, 1, \enclose{circle}{10}, \enclose{circle}{11}, 5, ...$

The sequence is characterized by the following properties:
The circled numbers are consecutive integers starting with $1$.
Immediately preceding each non-circled numbers $a_i$, there are exactly $\lfloor \sqrt{a_i} \rfloor$ adjacent circled numbers, where $\lfloor\,\rfloor$ is the floor function.
If we remove all circled numbers, the remaining numbers form a sequence identical to $S$, so $S$ is a fractal sequence.

Let $T(n)$ be the sum of the first $n$ elements of the sequence.

You are given $T(1) = 1$, $T(20) = 86$, $T(10^3) = 364089$ and $T(10^9) = 498676527978348241$.

Find $T(10^{18})$. Give the last $9$ digits of your answer.

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