#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 924: Larger Digit Permutation II.

Problem Statement:
    Let B(n) be the smallest number larger than n that can be formed by rearranging
    digits of n, or 0 if no such number exists. For example, B(245) = 254 and B(542) = 0.

    Define a_0 = 0 and a_n = a_{n - 1}^2 + 2 for n > 0.
    Let U(N) = sum from n=1 to N of B(a_n). You are given U(10) ≡ 543870437 (mod 10^9+7).

    Find U(10^16). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=924
"""
from typing import Any

euler_problem: int = 924
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'N': 10}, 'answer': None},
    {'category': 'extra', 'input': {'N': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
