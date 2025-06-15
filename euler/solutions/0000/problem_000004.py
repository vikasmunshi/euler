#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 4
# https://projecteuler.net/problem=4
# Answer: 
# Notes: 
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'size': 2},
        answer=9009,
    ),
    ProblemArgs(
        kwargs={'size': 3},
        answer=906609,
    ),
]


def is_palindromic(*, number: int) -> bool:
    number = str(number)
    return number == ''.join(reversed(number))


def solution(*, size: int) -> int:
    largest_palindrome = 0
    max_number = 10 ** size - 1
    min_number = 10 ** (size - 1)
    max_multiple_11 = max_number - (max_number % 11)
    for a in range(max_number, min_number, -1):
        a_is_multiple_11 = a % 11 == 0
        for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
            n = a * b
            if n <= largest_palindrome:
                break
            if is_palindromic(n):
                largest_palindrome = n

    return largest_palindrome


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent('''
solution to Project Euler problem 4
https://projecteuler.net/problem=4
A palindromic number reads the same both ways. The largest palindrome made from the product of two $2$-digit numbers is $9009 = 91 \times 99$.
Find the largest palindrome made from the product of two $3$-digit numbers.


''').strip()

if __name__ == '__main__':
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    timeout, max_workers = args.timeout, args.max_workers

    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
