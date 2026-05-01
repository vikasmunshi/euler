#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 337: Totient Stairstep Sequences.

Problem Statement:
    Let {a_1, a_2, ..., a_n} be an integer sequence of length n such that:
    a_1 = 6
    for all 1 ≤ i < n: phi(a_i) < phi(a_{i+1}) < a_i < a_{i+1}
    Let S(N) be the number of such sequences with a_n ≤ N.
    For example, S(10) = 4: {6}, {6, 8}, {6, 8, 9} and {6, 10}.
    We can verify that S(100) = 482073668 and S(10000) mod 10^8 = 73808307.
    Find S(20000000) mod 10^8.
    phi denotes Euler's totient function.

URL: https://projecteuler.net/problem=337
"""
from typing import Any

euler_problem: int = 337
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 20000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
