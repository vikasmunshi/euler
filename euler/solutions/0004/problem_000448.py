#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 448
# https://projecteuler.net/problem=448
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
solution to Project Euler problem 448
https://projecteuler.net/problem=448

The function $\operatorname{\mathbf{lcm}}(a,b)$ denotes the least common multiple of $a$ and $b$.

Let $A(n)$ be the average of the values of $\operatorname{lcm}(n,i)$ for $1 \le i \le n$.

E.g: $A(2)=(2+2)/2=2$ and $A(10)=(10+10+30+20+10+30+70+40+90+10)/10=32$. 

Let $S(n)=\sum A(k)$ for $1 \le k \le n$.

$S(100)=122726$.


Find $S(99999999019) \bmod 999999017$.


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