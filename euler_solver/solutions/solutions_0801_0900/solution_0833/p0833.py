#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 833: Square Triangle Products.

Problem Statement:
    Triangle numbers T_k are integers of the form k(k+1)/2.
    A few triangle numbers happen to be perfect squares like T_1=1 and T_8=36,
    but more can be found when considering the product of two triangle numbers.
    For example, T_2 * T_24 = 3 * 300 = 30^2.

    Let S(n) be the sum of c for all integer triples (a, b, c) with 0 < c <= n,
    c^2 = T_a * T_b and 0 < a < b.
    For example, S(100) = sqrt(T_1 T_8) + sqrt(T_2 T_24) + sqrt(T_1 T_49) + sqrt(T_3 T_48)
    = 6 + 30 + 35 + 84 = 155.

    You are given S(10^5) = 1479802 and S(10^9) = 241614948794.

    Find S(10^35). Give your answer modulo 136101521.

URL: https://projecteuler.net/problem=833
"""
from typing import Any

euler_problem: int = 833
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000000000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
