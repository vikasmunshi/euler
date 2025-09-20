#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 730: Shifted Pythagorean Triples.

Problem Statement:
    For a non-negative integer k, the triple (p,q,r) of positive integers is called a
    k-shifted Pythagorean triple if
        p^2 + q^2 + k = r^2

    (p, q, r) is said to be primitive if gcd(p, q, r) = 1.

    Let P_k(n) be the number of primitive k-shifted Pythagorean triples such that
    1 <= p <= q <= r and p + q + r <= n.

    For example, P_0(10^4) = 703 and P_20(10^4) = 1979.

    Define
        S(m,n) = sum_{k=0}^m P_k(n).

    You are given that S(10,10^4) = 10956.

    Find S(10^2,10^8).

URL: https://projecteuler.net/problem=730
"""
from typing import Any

euler_problem: int = 730
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 10, 'n': 10000}, 'answer': None},
    {'category': 'main', 'input': {'m': 100, 'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
