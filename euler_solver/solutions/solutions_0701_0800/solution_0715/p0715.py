#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 715: Sextuplet Norms.

Problem Statement:
    Let f(n) be the number of 6-tuples (x1,x2,x3,x4,x5,x6) such that:
        All xi are integers with 0 ≤ xi < n
        gcd(x1^2+x2^2+x3^2+x4^2+x5^2+x6^2, n^2) = 1

    Let G(n) = sum from k=1 to n of f(k) / (k^2 * φ(k))
    where φ(n) is Euler's totient function.

    For example, G(10) = 3053 and G(10^5) ≡ 157612967 mod 1,000,000,007.

    Find G(10^12) mod 1,000,000,007.

URL: https://projecteuler.net/problem=715
"""
from typing import Any

euler_problem: int = 715
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'nx1oKv/ZksdUMpMSN65dFiblc4wx1Vv+'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
