#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 419
# https://projecteuler.net/problem=419
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
solution to Project Euler problem 419
https://projecteuler.net/problem=419

The look and say sequence goes 1, 11, 21, 1211, 111221, 312211, 13112221, 1113213211, ...

The sequence starts with 1 and all other members are obtained by describing the previous member in terms of consecutive digits.

It helps to do this out loud:

1 is 'one one' → 11

11 is 'two ones' → 21

21 is 'one two and one one' → 1211 

1211 is 'one one, one two and two ones' → 111221

111221 is 'three ones, two twos and one one' → 312211

...


Define $A(n)$, $B(n)$ and $C(n)$ as the number of ones, twos and threes in the $n$'th element of the sequence respectively.

One can verify that $A(40) = 31254$, $B(40) = 20259$ and $C(40) = 11625$.


Find $A(n)$, $B(n)$ and $C(n)$ for $n = 10^{12}$.

Give your answer modulo $2^{30}$ and separate your values for $A$, $B$ and $C$ by a comma.

E.g. for $n = 40$ the answer would be 31254,20259,11625




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