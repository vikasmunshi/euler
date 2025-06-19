#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 851
# https://projecteuler.net/problem=851
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
solution to Project Euler problem 851
https://projecteuler.net/problem=851

Let $n$ be a positive integer and let $E_n$ be the set of $n$-tuples of strictly positive integers.


For $u = (u_1, \cdots, u_n)$ and $v = (v_1, \cdots, v_n)$ two elements of $E_n$, we define:


the Sum Of Products of $u$ and $v$, denoted by $\langle u, v\rangle$, as the sum $\displaystyle\sum_{i = 1}^n u_i v_i$;
the Product Of Sums of $u$ and $v$, denoted by $u \star v$, as the product $\displaystyle\prod_{i = 1}^n (u_i + v_i)$.


Let $R_n(M)$ be the sum of $u \star v$ over all ordered pairs $(u, v)$ in $E_n$ such that $\langle u, v\rangle = M$.

For example: $R_1(10) = 36$, $R_2(100) = 1873044$, $R_2(100!) \equiv 446575636 \bmod 10^9 + 7$.


Find $R_6(10000!)$. Give your answer modulo $10^9+7$.

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