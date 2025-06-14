#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 1
# https://projecteuler.net/problem=1
# Answer: 
# Notes: 
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_limit': 10},
        answer=23,
    ),
    ProblemArgs(
        kwargs={'max_limit': 1000},
        answer=233168,
    ),
]


def solution(*, max_limit: int) -> int:
    def sum_multiples(number: int) -> int:
        terms = (max_limit - 1) // number
        return number * terms * (terms + 1) // 2

    return sum_multiples(3) + sum_multiples(5) - sum_multiples(3 * 5)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent('''
solution to Project Euler problem 1
https://projecteuler.net/problem=1
If we list all the natural numbers below $10$ that are multiples of $3$ or $5$, we get $3, 5, 6$ and $9$. The sum of these multiples is $23$.
Find the sum of all the multiples of $3$ or $5$ below $1000$.

''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
