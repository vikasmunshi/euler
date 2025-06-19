#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 637
# https://projecteuler.net/problem=637
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
solution to Project Euler problem 637
https://projecteuler.net/problem=637

Given any positive integer $n$, we can construct a new integer by inserting plus signs between some of the digits of the base $B$ representation of $n$, and then carrying out the additions.


For example, from $n=123_{10}$  ($n$ in base $10$) we can construct the four base $10$ integers $123_{10}$,  $1+23=24_{10}$, $12+3=15_{10}$ and $1+2+3=6_{10}$.


Let $f(n,B)$ be the smallest number of steps needed to arrive at a single-digit number in base $B$. For example, $f(7,10)=0$ and $f(123,10)=1$.


Let $g(n,B_1,B_2)$ be the sum of the positive integers $i$ not exceeding $n$ such that $f(i,B_1)=f(i,B_2)$.


You are given $g(100,10,3)=3302$. 


Find $g(10^7,10,3)$.


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