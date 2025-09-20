#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 536: Modulo Power Identity.

Problem Statement:
    Let S(n) be the sum of all positive integers m not exceeding n having the
    following property:
        a^(m + 4) ≡ a (mod m) for all integers a.

    The values of m ≤ 100 that satisfy this property are 1, 2, 3, 5 and 21, thus
    S(100) = 1 + 2 + 3 + 5 + 21 = 32.
    You are given S(10^6) = 22868117.

    Find S(10^12).

URL: https://projecteuler.net/problem=536
"""
from typing import Any

euler_problem: int = 536
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
