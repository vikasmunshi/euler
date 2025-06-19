#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 382
# https://projecteuler.net/problem=382
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
solution to Project Euler problem 382
https://projecteuler.net/problem=382

A polygon is a flat shape consisting of straight line segments that are joined to form a closed chain or circuit. A polygon consists of at least three sides and does not self-intersect.



A set $S$ of positive numbers is said to generate a polygon $P$ if: no two sides of $P$ are the same length,
 the length of every side of $P$ is in $S$, and
 $S$ contains no other value.

For example:

The set $\{3, 4, 5\}$ generates a polygon with sides $3$, $4$, and $5$ (a triangle).

The set $\{6, 9, 11, 24\}$ generates a polygon with sides $6$, $9$, $11$, and $24$ (a quadrilateral).

The sets $\{1, 2, 3\}$ and $\{2, 3, 4, 9\}$ do not generate any polygon at all.



Consider the sequence $s$, defined as follows:$s_1 = 1$, $s_2 = 2$, $s_3 = 3$
$s_n = s_{n-1} + s_{n-3}$ for $n \gt 3$.

Let $U_n$ be the set $\{s_1, s_2, ..., s_n\}$. For example, $U_{10} = \{1, 2, 3, 4, 6, 9, 13, 19, 28, 41\}$.

Let $f(n)$ be the number of subsets of $U_n$ which generate at least one polygon.

For example, $f(5) = 7$, $f(10) = 501$ and $f(25) = 18635853$.



Find the last $9$ digits of $f(10^{18})$.


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