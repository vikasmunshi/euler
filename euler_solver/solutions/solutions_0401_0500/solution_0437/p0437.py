#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 437: Fibonacci Primitive Roots.

Problem Statement:
    When we calculate 8^n modulo 11 for n=0 to 9 we get: 1, 8, 9, 6, 4, 10, 3, 2, 5, 7.
    As we see all possible values from 1 to 10 occur. So 8 is a primitive root of 11.
    But there is more:
    If we take a closer look we see:
        1+8=9
        8+9=17 ≡ 6 mod 11
        9+6=15 ≡ 4 mod 11
        6+4=10
        4+10=14 ≡ 3 mod 11
        10+3=13 ≡ 2 mod 11
        3+2=5
        2+5=7
        5+7=12 ≡ 1 mod 11.
    So the powers of 8 mod 11 are cyclic with period 10, and
    8^n + 8^{n+1} ≡ 8^{n+2} (mod 11).
    8 is called a Fibonacci primitive root of 11.
    Not every prime has a Fibonacci primitive root.
    There are 323 primes less than 10000 with one or more Fibonacci primitive roots
    and the sum of these primes is 1480491.
    Find the sum of the primes less than 100000000 with at least one Fibonacci primitive root.

URL: https://projecteuler.net/problem=437
"""
from typing import Any

euler_problem: int = 437
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'R07ESBdfXcTO1U047AaD5GdR4KI='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
