#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 284
# https://projecteuler.net/problem=284
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
solution to Project Euler problem 284
https://projecteuler.net/problem=284
The 3-digit number 376 in the decimal numbering system is an example of numbers with the special property that its square ends with the same digits: 3762 = 141376. Let's call a number with this property a steady square.

Steady squares can also be observed in other numbering systems. In the base 14 numbering system, the 3-digit number c37 is also a steady square: c372 = aa0c37, and the sum of its digits is c+3+7=18 in the same numbering system. The letters a, b, c and d are used for the 10, 11, 12 and 13 digits respectively, in a manner similar to the hexadecimal numbering system.

For 1 ≤ n ≤ 9, the sum of the digits of all the n-digit steady squares in the base 14 numbering system is 2d8 (582 decimal). Steady squares with leading 0's are not allowed.

Find the sum of the digits of all the n-digit steady squares in the base 14 numbering system for

1 ≤ n ≤ 10000 (decimal) and give your answer in the base 14 system using lower case letters where necessary.

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