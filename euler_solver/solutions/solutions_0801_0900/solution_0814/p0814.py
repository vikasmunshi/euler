#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 814: Mezzo-forte.

Problem Statement:
    4n people stand in a circle with their heads down. When the bell rings they
    all raise their heads and either look at the person immediately to their
    left, the person immediately to their right or the person diametrically
    opposite. If two people find themselves looking at each other they both
    scream.

    Define S(n) to be the number of ways that exactly half of the people scream.
    You are given S(1) = 48 and S(10) ≡ 420121075 mod 998244353.

    Find S(10^3). Enter your answer modulo 998244353.

URL: https://projecteuler.net/problem=814
"""
from typing import Any

euler_problem: int = 814
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
