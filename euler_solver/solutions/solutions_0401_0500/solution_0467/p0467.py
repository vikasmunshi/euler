#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 467: Superinteger.

Problem Statement:
    An integer s is called a superinteger of another integer n if the digits of n
    form a subsequence of the digits of s. For example, 2718281828 is a superinteger
    of 18828, while 314159 is not a superinteger of 151.

    Let p(n) be the nth prime number, and let c(n) be the nth composite number. For
    example, p(1) = 2, p(10) = 29, c(1) = 4 and c(10) = 18.
    {p(i) : i >= 1} = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...}
    {c(i) : i >= 1} = {4, 6, 8, 9, 10, 12, 14, 15, 16, 18, ...}

    Let P^D be the sequence of the digital roots of {p(i)} (C^D is defined similarly
    for {c(i)}):
    P^D = {2, 3, 5, 7, 2, 4, 8, 1, 5, 2, ...}
    C^D = {4, 6, 8, 9, 1, 3, 5, 6, 7, 9, ...}

    Let P_n be the integer formed by concatenating the first n elements of P^D (C_n
    is defined similarly for C^D).
    P_10 = 2357248152
    C_10 = 4689135679

    Let f(n) be the smallest positive integer that is a common superinteger of P_n
    and C_n. For example, f(10) = 2357246891352679, and f(100) mod 1000000007 = 771661825.

    Find f(10000) mod 1000000007.

URL: https://projecteuler.net/problem=467
"""
from typing import Any

euler_problem: int = 467
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
