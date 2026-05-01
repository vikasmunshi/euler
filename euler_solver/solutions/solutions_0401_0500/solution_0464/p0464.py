#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 464: Möbius Function and Intervals.

Problem Statement:
    The Möbius function, denoted μ(n), is defined as:
        μ(n) = (-1)^ω(n) if n is squarefree (ω(n) is the number of distinct prime factors)
        μ(n) = 0 if n is not squarefree.

    Let P(a, b) be the number of integers n in [a, b] with μ(n) = 1.
    Let N(a, b) be the number of integers n in [a, b] with μ(n) = -1.
    For example, P(2,10) = 2 and N(2,10) = 4.

    Let C(n) be the number of integer pairs (a, b) with:
        1 ≤ a ≤ b ≤ n,
        99 * N(a, b) ≤ 100 * P(a, b), and
        99 * P(a, b) ≤ 100 * N(a, b).

    For example, C(10) = 13, C(500) = 16676, and C(10_000) = 20155319.

    Find C(20_000_000).

URL: https://projecteuler.net/problem=464
"""
from typing import Any

euler_problem: int = 464
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 20000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 50000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
