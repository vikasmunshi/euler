#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 446: Retractions B.

Problem Statement:
    For every integer n>1, the family of functions f_{n,a,b} is defined by
    f_{n,a,b}(x) ≡ a x + b mod n where a,b,x are integers and 0 < a < n, 0 ≤ b < n,
    0 ≤ x < n.

    We will call f_{n,a,b} a retraction if f_{n,a,b}(f_{n,a,b}(x)) ≡ f_{n,a,b}(x) mod n
    for every 0 ≤ x < n.
    Let R(n) be the number of retractions for n.

    F(N) = ∑_{n=1}^N R(n^4 + 4).
    F(1024) = 77532377300600.

    Find F(10^7).
    Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=446
"""
from typing import Any

euler_problem: int = 446
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'N': 10000000}, 'answer': None},
    {'category': 'dev', 'input': {'N': 1024}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
