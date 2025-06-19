#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 947
# https://projecteuler.net/problem=947
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
solution to Project Euler problem 947
https://projecteuler.net/problem=947

The $(a,b,m)$-sequence, where $0 \leq a,b \lt m$, is defined as


$\begin{align*}
g(0)&=a\\
g(1)&=b\\
g(n)&= \big(g(n-1) + g(n-2)\big) \bmod m
\end{align*}$



All $(a,b,m)$-sequences are periodic with period denoted by $p(a,b,m)$.
 
The first few terms of the $(0,1,8)$-sequence are $(0,1,1,2,3,5,0,5,5,2,7,1,0,1,1,2,\ldots )$ and so $p(0,1,8)=12$.


Let $\displaystyle s(m)=\sum_{a=0}^{m-1}\sum_{b=0}^{m-1} p(a,b,m)^2$. For example, $s(3)=513$ and $s(10)=225820$.


Define $\displaystyle S(M)=\sum_{m=1}^{M}s(m)$. You are given, $S(3)=542$ and $S(10)=310897$.


Find $S(10^6)$. Give your answer modulo $999\,999\,893$.


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