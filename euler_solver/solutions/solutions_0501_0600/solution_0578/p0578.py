#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 578: Integers with Decreasing Prime Powers.

Problem Statement:
    Any positive integer can be written as a product of prime powers:
    p_1^{a_1} × p_2^{a_2} × ... × p_k^{a_k},
    where p_i are distinct prime integers, a_i > 0 and p_i < p_j if i < j.

    A decreasing prime power positive integer is one for which a_i ≥ a_j if i < j.
    For example, 1, 2, 15=3×5, 360=2^3 × 3^2 × 5 and 1000=2^3 × 5^3 are
    decreasing prime power integers.

    Let C(n) be the count of decreasing prime power positive integers not
    exceeding n.
    C(100) = 94 since all positive integers not exceeding 100 have decreasing
    prime powers except 18, 50, 54, 75, 90 and 98.
    You are given C(10^6) = 922052.

    Find C(10^{13}).

URL: https://projecteuler.net/problem=578
"""
from typing import Any

euler_problem: int = 578
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
