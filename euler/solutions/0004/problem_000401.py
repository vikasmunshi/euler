#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 401
# https://projecteuler.net/problem=401
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
solution to Project Euler problem 401
https://projecteuler.net/problem=401

The divisors of $6$ are $1,2,3$ and $6$.

The sum of the squares of these numbers is $1+4+9+36=50$.


Let $\operatorname{sigma}_2(n)$ represent the sum of the squares of the divisors of $n$.
Thus $\operatorname{sigma}_2(6)=50$.

Let $\operatorname{SIGMA}_2$ represent the summatory function of $\operatorname{sigma}_2$, that is $\operatorname{SIGMA}_2(n)=\sum \operatorname{sigma}_2(i)$ for $i=1$ to $n$.

The first $6$ values of $\operatorname{SIGMA}_2$ are: $1,6,16,37,63$ and $113$.


Find $\operatorname{SIGMA}_2(10^{15})$ modulo $10^9$. 


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