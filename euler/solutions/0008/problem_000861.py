#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 861
# https://projecteuler.net/problem=861
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
solution to Project Euler problem 861
https://projecteuler.net/problem=861
A unitary divisor of a positive integer $n$ is a divisor $d$ of $n$ such that $\gcd\left(d,\frac{n}{d}\right)=1$.

A bi-unitary divisor of $n$ is a divisor $d$ for which $1$ is the only unitary divisor of $d$ that is also a unitary divisor of $\frac{n}{d}$.

For example, $2$ is a bi-unitary divisor of $8$, because the unitary divisors of $2$ are $\{1,2\}$, and the unitary divisors of $8/2$ are $\{1,4\}$, with $1$ being the only unitary divisor in common.

The bi-unitary divisors of $240$ are $\{1,2,3,5,6,8,10,15,16,24,30,40,48,80,120,240\}$.

Let $P(n)$ be the product of all bi-unitary divisors of $n$. Define $Q_k(N)$ as the number of positive integers $1 \lt n \leq N$ such that $P(n)=n^k$. For example, $Q_2\left(10^2\right)=51$ and $Q_6\left(10^6\right)=6189$.

Find $\sum_{k=2}^{10}Q_k\left(10^{12}\right)$.


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