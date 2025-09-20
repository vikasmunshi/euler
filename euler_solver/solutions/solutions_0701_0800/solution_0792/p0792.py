#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 792: Too Many Twos.

Problem Statement:
    We define ν₂(n) to be the largest integer r such that 2^r divides n. For example,
    ν₂(24) = 3.

    Define S(n) = sum from k = 1 to n of (-2)^k * C(2k, k) and u(n) = ν₂(3S(n) + 4).

    For example, when n = 4 then S(4) = 980 and 3S(4) + 4 = 2944 = 2^7 * 23, hence u(4) = 7.
    You are also given u(20) = 24.

    Also define U(N) = sum from n = 1 to N of u(n^3). You are given U(5) = 241.

    Find U(10^4).

URL: https://projecteuler.net/problem=792
"""
from typing import Any

euler_problem: int = 792
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 5}, 'answer': None},
    {'category': 'main', 'input': {'N': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
