#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 196
# https://projecteuler.net/problem=196
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
solution to Project Euler problem 196
https://projecteuler.net/problem=196
Build a triangle from all positive integers in the following way:

 1

 2  3

 4  5  6

 7  8  9 10
11 12 13 14 15

16 17 18 19 20 21

22 23 24 25 26 27 28
29 30 31 32 33 34 35 36
37 38 39 40 41 42 43 44 45

46 47 48 49 50 51 52 53 54 55

56 57 58 59 60 61 62 63 64 65 66

. . .

Each positive integer has up to eight neighbours in the triangle.

A set of three primes is called a prime triplet if one of the three primes has the other two as neighbours in the triangle.

For example, in the second row, the prime numbers $2$ and $3$ are elements of some prime triplet.

If row $8$ is considered, it contains two primes which are elements of some prime triplet, i.e. $29$ and $31$.

If row $9$ is considered, it contains only one prime which is an element of some prime triplet: $37$.

Define $S(n)$ as the sum of the primes in row $n$ which are elements of any prime triplet.

Then $S(8)=60$ and $S(9)=37$.

You are given that $S(10000)=950007619$.

Find $S(5678027) + S(7208785)$.


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