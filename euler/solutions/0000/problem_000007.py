#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 7
# https://projecteuler.net/problem=7
# Answer: answers={6: 13, 10001: 104743}
# Notes: 
import textwrap
from math import log

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 6},
        answer=13,
    ),
    ProblemArgs(
        kwargs={'n': 10001},
        answer=104743,
    ),
]


def solution(*, n: int) -> int:
    if n == 1:
        return 2
    max_expected_value = int(n * log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not a prime as 0
            except IndexError:
                break
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 7
https://projecteuler.net/problem=7
By listing the first six prime numbers: $2, 3, 5, 7, 11$, and $13$, we can see that the $6$th prime is $13$.
What is the $10\,001$st prime number?


''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
