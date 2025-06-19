#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 374
# https://projecteuler.net/problem=374
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
solution to Project Euler problem 374
https://projecteuler.net/problem=374
An integer partition of a number $n$ is a way of writing $n$ as a sum of positive integers.

Partitions that differ only in the order of their summands are considered the same.
A partition of $n$ into distinct parts is a partition of $n$ in which every part occurs at most once.

The partitions of $5$ into distinct parts are:

$5$, $4+1$ and $3+2$.

Let $f(n)$ be the maximum product of the parts of any such partition of $n$ into distinct parts and let $m(n)$ be the number of elements of any such partition of $n$ with that product.

So $f(5)=6$ and $m(5)=2$.

For $n=10$ the partition with the largest product is $10=2+3+5$, which gives $f(10)=30$ and $m(10)=3$.

And their product, $f(10) \cdot m(10) = 30 \cdot 3 = 90$.

It can be verified that

$\sum f(n) \cdot m(n)$ for $1 \le n \le 100 = 1683550844462$.

Find $\sum f(n) \cdot m(n)$ for $1 \le n \le 10^{14}$.

Give your answer modulo $982451653$, the $50$ millionth prime.


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