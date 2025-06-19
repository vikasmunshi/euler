#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 302
# https://projecteuler.net/problem=302
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
solution to Project Euler problem 302
https://projecteuler.net/problem=302

A positive integer $n$ is powerful if $p^2$ is a divisor of $n$ for every prime factor $p$ in $n$.


A positive integer $n$ is a perfect power if $n$ can be expressed as a power of another positive integer.


A positive integer $n$ is an Achilles number if $n$ is powerful but not a perfect power. For example, $864$ and $1800$ are Achilles numbers: $864 = 2^5 \cdot 3^3$ and $1800 = 2^3 \cdot 3^2 \cdot 5^2$.


We shall call a positive integer $S$ a Strong Achilles number if both $S$ and $\phi(S)$ are Achilles numbers.1

For example, $864$ is a Strong Achilles number: $\phi(864) = 288 = 2^5 \cdot 3^2$. However, $1800$ isn't a Strong Achilles number because: $\phi(1800) = 480 = 2^5 \cdot 3^1 \cdot 5^1$.

There are $7$ Strong Achilles numbers below $10^4$ and $656$ below $10^8$.


How many Strong Achilles numbers are there below $10^{18}$?


1 $\phi$ denotes Euler's totient function.







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