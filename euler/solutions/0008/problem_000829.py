#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 829
# https://projecteuler.net/problem=829
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
solution to Project Euler problem 829
https://projecteuler.net/problem=829
Given any integer $n \gt 1$ a binary factor tree $T(n)$ is defined to be:

A tree with the single node $n$ when $n$ is prime.
A binary tree that has root node $n$, left subtree $T(a)$ and right subtree $T(b)$, when $n$ is not prime. Here $a$ and $b$ are positive integers such that $n = ab$, $a\le b$ and $b-a$ is the smallest.

For example $T(20)$:


We define $M(n)$ to be the smallest number that has a factor tree identical in shape to the factor tree for $n!!$, the double factorial of $n$.

For example, consider $9!! = 9\times 7\times 5\times 3\times 1 = 945$. The factor tree for $945$ is shown below together with the factor tree for $72$ which is the smallest number that has a factor tree of the same shape. Hence $M(9) = 72$.


Find $\displaystyle\sum_{n=2}^{31} M(n)$.


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