#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 323
# https://projecteuler.net/problem=323
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
solution to Project Euler problem 323
https://projecteuler.net/problem=323
Let $y_0, y_1, y_2, ...$ be a sequence of random unsigned $32$-bit integers

(i.e. $0 \le y_i \lt 2^{32}$, every value equally likely).
For the sequence $x_i$ the following recursion is given:
$x_0 = 0$ and
$x_i = x_{i - 1} \boldsymbol \mid y_{i - 1}$, for $i \gt 0$. ($\boldsymbol \mid$ is the bitwise-OR operator).
It can be seen that eventually there will be an index $N$ such that $x_i = 2^{32} - 1$ (a bit-pattern of all ones) for all $i \ge N$.

Find the expected value of $N$. 

Give your answer rounded to $10$ digits after the decimal point.

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