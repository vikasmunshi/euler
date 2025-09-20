#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 889: Rational Blancmange.

Problem Statement:
    Recall the blancmange function from Problem 226: T(x) = sum for n=0 to infinity of
    s(2^n x) / 2^n, where s(x) is the distance from x to the nearest integer.

    For positive integers k, t, r, we write
    F(k, t, r) = (2^(2k) - 1) * T( ((2^t + 1)^r) / (2^k + 1) ).
    It can be shown that F(k, t, r) is always an integer.
    For example, F(3, 1, 1) = 42, F(13, 3, 3) = 23093880 and
    F(103, 13, 6) ≡ 878922518 mod 1,000,062,031.

    Find F(10^18 + 31, 10^14 + 31, 62). Give your answer modulo 1,000,062,031.

URL: https://projecteuler.net/problem=889
"""
from typing import Any

euler_problem: int = 889
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3, 't': 1, 'r': 1}, 'answer': None},
    {'category': 'main', 'input': {'k': 1000000000000000031, 't': 100000000000031, 'r': 62}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
