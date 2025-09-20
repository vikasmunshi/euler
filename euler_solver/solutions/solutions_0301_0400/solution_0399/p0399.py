#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 399: Squarefree Fibonacci Numbers.

Problem Statement:
    The first 15 Fibonacci numbers are:
    1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610.
    It can be seen that 8 and 144 are not squarefree: 8 is divisible by 4
    and 144 is divisible by 4 and by 9.
    So the first 13 squarefree Fibonacci numbers are:
    1, 1, 2, 3, 5, 13, 21, 34, 55, 89, 233, 377 and 610.

    The 200th squarefree Fibonacci number is:
    971183874599339129547649988289594072811608739584170445.
    The last sixteen digits of this number are: 1608739584170445 and in
    scientific notation this number can be written as 9.7e53.

    Find the 100000000th squarefree Fibonacci number.
    Give as your answer its last sixteen digits followed by a comma followed
    by the number in scientific notation (rounded to one digit after the decimal).
    For the 200th squarefree number the answer would have been:
    1608739584170445,9.7e53

    Note:
    For this problem, assume that for every prime p, the first Fibonacci number
    divisible by p is not divisible by p^2 (this is part of Wall's conjecture).
    This has been verified for primes ≤ 3·10^15, but has not been proven in general.
    If it happens that the conjecture is false, then the accepted answer to this problem
    isn't guaranteed to be the 100000000th squarefree Fibonacci number, rather it
    represents only a lower bound for that number.

URL: https://projecteuler.net/problem=399
"""
from typing import Any

euler_problem: int = 399
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 13}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'jNhU6Y/qx3CXNn8Z'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
