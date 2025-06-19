#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 143
# https://projecteuler.net/problem=143
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
solution to Project Euler problem 143
https://projecteuler.net/problem=143
Let $ABC$ be a triangle with all interior angles being less than $120$ degrees. Let $X$ be any point inside the triangle and let $XA = p$, $XC = q$, and $XB = r$.
Fermat challenged Torricelli to find the position of $X$ such that $p + q + r$ was minimised.
Torricelli was able to prove that if equilateral triangles $AOB$, $BNC$ and $AMC$ are constructed on each side of triangle $ABC$, the circumscribed circles of $AOB$, $BNC$, and $AMC$ will intersect at a single point, $T$, inside the triangle. Moreover he proved that $T$, called the Torricelli/Fermat point, minimises $p + q + r$. Even more remarkable, it can be shown that when the sum is minimised, $AN = BM = CO = p + q + r$ and that $AN$, $BM$ and $CO$ also intersect at $T$.

If the sum is minimised and $a, b, c, p, q$ and $r$ are all positive integers we shall call triangle $ABC$ a Torricelli triangle. For example, $a = 399$, $b = 455$, $c = 511$ is an example of a Torricelli triangle, with $p + q + r = 784$.
Find the sum of all distinct values of $p + q + r \le 120000$ for Torricelli triangles.


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