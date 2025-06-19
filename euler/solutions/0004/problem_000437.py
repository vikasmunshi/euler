#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 437
# https://projecteuler.net/problem=437
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
solution to Project Euler problem 437
https://projecteuler.net/problem=437

When we calculate $8^n$ modulo $11$ for $n=0$ to $9$ we get: $1, 8, 9, 6, 4, 10, 3, 2, 5, 7$.

As we see all possible values from $1$ to $10$ occur. So $8$ is a primitive root of $11$.

But there is more:

If we take a closer look we see:

$1+8=9$

$8+9=17 \equiv 6 \bmod 11$

$9+6=15 \equiv 4 \bmod 11$

$6+4=10$

$4+10=14 \equiv 3 \bmod 11$

$10+3=13 \equiv 2 \bmod 11$

$3+2=5$

$2+5=7$

$5+7=12 \equiv 1 \bmod 11$.

So the powers of $8 \bmod 11$ are cyclic with period $10$, and $8^n + 8^{n+1} \equiv 8^{n+2} \pmod{11}$.

$8$ is called a Fibonacci primitive root of $11$.

Not every prime has a Fibonacci primitive root.

There are $323$ primes less than $10000$ with one or more Fibonacci primitive roots and the sum of these primes is $1480491$.

Find the sum of the primes less than $100\,000\,000$ with at least one Fibonacci primitive root.



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