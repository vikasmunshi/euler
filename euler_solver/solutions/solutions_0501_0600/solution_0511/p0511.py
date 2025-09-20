#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 511: Sequences with Nice Divisibility Properties.

Problem Statement:
    Let Seq(n,k) be the number of positive-integer sequences {a_i}_{1 ≤ i ≤ n}
    of length n such that:
        - n is divisible by a_i for 1 ≤ i ≤ n, and
        - n + a_1 + a_2 + ... + a_n is divisible by k.

    Examples:
    Seq(3,4) = 4, and the 4 sequences are:
        {1, 1, 3}
        {1, 3, 1}
        {3, 1, 1}
        {3, 3, 3}

    Seq(4,11) = 8, and the 8 sequences are:
        {1, 1, 1, 4}
        {1, 1, 4, 1}
        {1, 4, 1, 1}
        {4, 1, 1, 1}
        {2, 2, 2, 1}
        {2, 2, 1, 2}
        {2, 1, 2, 2}
        {1, 2, 2, 2}

    The last nine digits of Seq(1111,24) are 840643584.

    Find the last nine digits of Seq(1234567898765,4321).

URL: https://projecteuler.net/problem=511
"""
from typing import Any

euler_problem: int = 511
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'k': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 1234567898765, 'k': 4321}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1111, 'k': 24}, 'answer': None},
]
encrypted: str = (
    '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'
    'FjMDcA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
