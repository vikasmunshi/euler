#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 675: 2^{ω(n)}.

Problem Statement:
    Let ω(n) denote the number of distinct prime divisors of a positive integer n.
    So ω(1) = 0 and ω(360) = ω(2^3 × 3^2 × 5) = 3.

    Let S(n) be the sum of 2^{ω(d)} over all divisors d of n.
    E.g. S(6) = 2^{ω(1)} + 2^{ω(2)} + 2^{ω(3)} + 2^{ω(6)} = 2^0 + 2^1 + 2^1 + 2^2 = 9.

    Let F(n) = sum from i=2 to n of S(i!).
    F(10) = 4821.

    Find F(10,000,000). Give your answer modulo 1,000,000,087.

URL: https://projecteuler.net/problem=675
"""
from typing import Any

euler_problem: int = 675
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ry77KuX493MAOxrL9NpVyHhA1+o='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
