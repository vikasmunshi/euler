#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 833
# https://projecteuler.net/problem=833
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
solution to Project Euler problem 833
https://projecteuler.net/problem=833
Triangle numbers $T_k$ are integers of the form $\frac{k(k+1)} 2$.

A few triangle numbers happen to be perfect squares like $T_1=1$ and $T_8=36$, but more can be found when considering the product of two triangle numbers. For example, $T_2 \cdot T_{24}=3 \cdot 300=30^2$.

Let $S(n)$ be the sum of $c$ for all integers triples $(a, b, c)$ with $0<c \le n$, $c^2=T_a \cdot T_b$ and $0<a<b$.
For example, $S(100)= \sqrt{T_1 T_8}+\sqrt{T_2 T_{24}}+\sqrt{T_1 T_{49}}+\sqrt{T_3 T_{48}}=6+30+35+84=155$.

You are given $S(10^5)=1479802$ and $S(10^9)=241614948794$.

Find $S(10^{35})$. Give your answer modulo $136101521$.

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