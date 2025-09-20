#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 915: Giant GCDs.

Problem Statement:
    The function s(n) is defined recursively for positive integers by
    s(1) = 1 and s(n+1) = (s(n) - 1)^3 + 2 for n ≥ 1.
    The sequence begins: s(1) = 1, s(2) = 2, s(3) = 3, s(4) = 10, ...

    For positive integers N, define
        T(N) = sum_{a=1}^N sum_{b=1}^N gcd(s(s(a)), s(s(b))).
    You are given T(3) = 12, T(4) ≡ 24881925 and T(100) ≡ 14416749 both modulo 123456789.

    Find T(10^8). Give your answer modulo 123456789.

URL: https://projecteuler.net/problem=915
"""
from typing import Any

euler_problem: int = 915
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
