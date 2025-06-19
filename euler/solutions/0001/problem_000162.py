#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 162
# https://projecteuler.net/problem=162
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
solution to Project Euler problem 162
https://projecteuler.net/problem=162
In the hexadecimal number system numbers are represented using $16$ different digits:
$$0,1,2,3,4,5,6,7,8,9,\mathrm A,\mathrm B,\mathrm C,\mathrm D,\mathrm E,\mathrm F.$$
The hexadecimal number $\mathrm{AF}$ when written in the decimal number system equals $10 \times 16 + 15 = 175$.
In the $3$-digit hexadecimal numbers $10\mathrm A$, $1\mathrm A0$, $\mathrm A10$, and $\mathrm A01$ the digits $0$, $1$ and $\mathrm A$ are all present.

Like numbers written in base ten we write hexadecimal numbers without leading zeroes.
How many hexadecimal numbers containing at most sixteen hexadecimal digits exist with all of the digits $0$, $1$, and $\mathrm A$ present at least once?

Give your answer as a hexadecimal number.
(A, B, C, D, E and F in upper case, without any leading or trailing code that marks the number as hexadecimal and without leading zeroes, e.g. 1A3F and not: 1a3f and not 0x1a3f and not $1A3F and not #1A3F and not 0000001A3F)

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