#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 456
# https://projecteuler.net/problem=456
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
solution to Project Euler problem 456
https://projecteuler.net/problem=456
Define:
$x_n = (1248^n \bmod 32323) - 16161$
$y_n = (8421^n \bmod 30103) - 15051$

$P_n = \{(x_1, y_1), (x_2, y_2), ..., (x_n, y_n)\}$


For example, $P_8 = \{(-14913, -6630),$$(-10161, 5625),$$(5226, 11896),$$(8340, -10778),$$(15852, -5203),$$(-15165, 11295),$$(-1427, -14495),$$(12407, 1060)\}$.

Let $C(n)$ be the number of triangles whose vertices are in $P_n$ which contain the origin in the interior.


Examples:

$C(8) = 20$

$C(600) = 8950634$

$C(40\,000) = 2666610948988$


Find $C(2\,000\,000)$.


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