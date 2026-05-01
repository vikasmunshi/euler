#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 421: Prime Factors of n^15+1.

Problem Statement:
    Numbers of the form n^15+1 are composite for every integer n > 1.
    For positive integers n and m let s(n,m) be defined as the sum of the
    distinct prime factors of n^15+1 not exceeding m.

    E.g. 2^15+1 = 3 x 3 x 11 x 331.
    So s(2,10) = 3 and s(2,1000) = 3+11+331 = 345.

    Also 10^15+1 = 7 x 11 x 13 x 211 x 241 x 2161 x 9091.
    So s(10,100) = 31 and s(10,1000) = 483.
    Find sum s(n,10^8) for 1 <= n <= 10^11.

URL: https://projecteuler.net/problem=421
"""
from typing import Any

euler_problem: int = 421
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
