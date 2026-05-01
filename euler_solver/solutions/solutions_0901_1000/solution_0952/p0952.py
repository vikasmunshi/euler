#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 952: Order Modulo Factorial.

Problem Statement:
    Given a prime p and a positive integer n < p, let R(p, n) be the multiplicative order
    of p modulo n!.

    In other words, R(p, n) is the minimal positive integer r such that

        p^r ≡ 1 (mod n!)

    For example, R(7, 4) = 2 and R(10^9 + 7, 12) = 17280.

    Find R(10^9 + 7, 10^7). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=952
"""
from typing import Any

euler_problem: int = 952
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 7, 'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'p': 1000000007, 'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
