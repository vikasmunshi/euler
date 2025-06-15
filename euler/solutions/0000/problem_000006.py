#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 6
# https://projecteuler.net/problem=6
# Answer: answers={10: 2640, 100: 25164150}
# Notes: 
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 10},
        answer=2640,
    ),
    ProblemArgs(
        kwargs={'n': 100},
        answer=25164150,
    ),
]


def solution(*, n: int) -> int:
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 6
https://projecteuler.net/problem=6
The sum of the squares of the first ten natural numbers is,
$$1^2 + 2^2 + ... + 10^2 = 385.$$
The square of the sum of the first ten natural numbers is,
$$(1 + 2 + ... + 10)^2 = 55^2 = 3025.$$
Hence the difference between the sum of the squares of the first ten natural numbers and the square of the sum is $3025 - 385 = 2640$.
Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.

''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
