#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 647
# https://projecteuler.net/problem=647
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
solution to Project Euler problem 647
https://projecteuler.net/problem=647

It is possible to find positive integers $A$ and $B$ such that given any triangular number, $T_n$, then $AT_n +B$ is always a triangular number. We define $F_3(N)$ to be the sum of $(A+B)$ over all such possible pairs $(A,B)$ with $\max(A,B)\le N$. For example $F_3(100) = 184$.


Polygonal numbers are generalisations of triangular numbers. Polygonal numbers with parameter $k$ we call $k$-gonal numbers. The formula for the $n$th $k$-gonal number is $\frac 12n\big(n(k-2)+4-k\big)$ where $n \ge 1$. For example when $k = 3$ we get $\frac 12n(n+1)$ the formula for triangular numbers.


The statement above is true for pentagonal, heptagonal and in fact any $k$-gonal number with $k$ odd. For example when $k=5$ we get the pentagonal numbers and we can find positive integers $A$ and $B$ such that given any pentagonal number, $P_n$, then $AP_n+B$ is always a pentagonal number. We define $F_5(N)$ to be the sum of $(A+B)$ over all such possible pairs $(A,B)$ with $\max(A,B)\le N$.


Similarly we define $F_k(N)$ for odd $k$. You are given $\sum_{k} F_k(10^3) = 14993$ where the sum is over all odd $k = 3,5,7,\ldots$.


Find $\sum_{k} F_k(10^{12})$ where the sum is over all odd $k = 3,5,7,\ldots$


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