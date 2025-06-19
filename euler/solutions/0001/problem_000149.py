#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 149
# https://projecteuler.net/problem=149
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
solution to Project Euler problem 149
https://projecteuler.net/problem=149
Looking at the table below, it is easy to verify that the maximum possible sum of adjacent numbers in any direction (horizontal, vertical, diagonal or anti-diagonal) is $16$ ($= 8 + 7 + 1$).


$-2$$5$$3$$2$$9$$-6$$5$$1$$3$$2$$7$$3$$-1$$8$$-4$$8$

Now, let us repeat the search, but on a much larger scale:

First, generate four million pseudo-random numbers using a specific form of what is known as a "Lagged Fibonacci Generator":

For $1 \le k \le 55$, $s_k = [100003 - 200003 k + 300007 k^3] \pmod{1000000} - 500000$.

For $56 \le k \le 4000000$, $s_k = [s_{k-24} + s_{k - 55} + 1000000] \pmod{1000000} - 500000$.

Thus, $s_{10} = -393027$ and $s_{100} = 86613$.

The terms of $s$ are then arranged in a $2000 \times 2000$ table, using the first $2000$ numbers to fill the first row (sequentially), the next $2000$ numbers to fill the second row, and so on.

Finally, find the greatest sum of (any number of) adjacent entries in any direction (horizontal, vertical, diagonal or anti-diagonal).

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