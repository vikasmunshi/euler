#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 5
# https://projecteuler.net/problem=5
# Answer: 
# Notes: 
import textwrap
from functools import reduce
from math import gcd

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},
        answer=2520,
    ),
    ProblemArgs(
        kwargs={'n': 20},
        answer=232792560,
    ),
]


def solution(*, n: int) -> int:
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent('''
solution to Project Euler problem 5
https://projecteuler.net/problem=5
$2520$ is the smallest number that can be divided by each of the numbers from $1$ to $10$ without any remainder.
What is the smallest positive number that is evenly divisibledivisible with no remainder by all of the numbers from $1$ to $20$?


''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
