#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 447: Retractions C.

Problem Statement:
    For every integer n > 1, the family of functions f_{n,a,b} is defined
    by
        f_{n,a,b}(x) ≡ a x + b mod n
    for a,b,x integer and 0 < a < n, 0 ≤ b < n, 0 ≤ x < n.

    We will call f_{n,a,b} a retraction if
        f_{n,a,b}(f_{n,a,b}(x)) ≡ f_{n,a,b}(x) mod n
    for every 0 ≤ x < n.

    Let R(n) be the number of retractions for n.

    F(N) = sum from n=2 to N of R(n).

    F(10^7) ≡ 638042271 mod 1,000,000,007.

    Find F(10^14).
    Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=447
"""
from typing import Any

euler_problem: int = 447
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'oQXCuUXG3v480QzRIhu6XjXV2Jnur0hw7+ZoDA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
