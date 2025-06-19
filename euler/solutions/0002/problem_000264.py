#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 264
# https://projecteuler.net/problem=264
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
solution to Project Euler problem 264
https://projecteuler.net/problem=264
Consider all the triangles having:
All their vertices on lattice pointsInteger coordinates.
CircumcentreCentre of the circumscribed circle at the origin $O$.
OrthocentrePoint where the three altitudes meet at the point $H(5, 0)$.
There are nine such triangles having a perimeter $\le 50$.

Listed and shown in ascending order of their perimeter, they are:

$A(-4, 3)$, $B(5, 0)$, $C(4, -3)$

$A(4, 3)$, $B(5, 0)$, $C(-4, -3)$

$A(-3, 4)$, $B(5, 0)$, $C(3, -4)$



$A(3, 4)$, $B(5, 0)$, $C(-3, -4)$

$A(0, 5)$, $B(5, 0)$, $C(0, -5)$

$A(1, 8)$, $B(8, -1)$, $C(-4, -7)$



$A(8, 1)$, $B(1, -8)$, $C(-4, 7)$

$A(2, 9)$, $B(9, -2)$, $C(-6, -7)$

$A(9, 2)$, $B(2, -9)$, $C(-6, 7)$




The sum of their perimeters, rounded to four decimal places, is $291.0089$.

Find all such triangles with a perimeter $\le 10^5$.

Enter as your answer the sum of their perimeters rounded to four decimal places.


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