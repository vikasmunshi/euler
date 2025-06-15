#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 3
# https://projecteuler.net/problem=3
# Answer: 
# Notes: 
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'number': 13195},
        answer=29,
    ),
    ProblemArgs(
        kwargs={'number': 600851475143},
        answer=6857,
    ),
]


def reduce(num: int, divisor: int) -> int:
    num //= divisor
    while num % divisor == 0:
        num //= divisor
    return num


def solution(*, number: int) -> int:
    number, last_factor = (reduce(number, 2), 2) if number % 2 == 0 else (number, 1)
    factor, max_factor = 3, int(number ** 0.5)
    while number > 1 and factor < max_factor:
        if number % factor == 0:
            number, last_factor = reduce(number, factor), factor
            max_factor = int(number ** 0.5)
        factor += 2

    return last_factor if number == 1 else number


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent('''
solution to Project Euler problem 3
https://projecteuler.net/problem=3
The prime factors of $13195$ are $5, 7, 13$ and $29$.
What is the largest prime factor of the number $600851475143$?



''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
