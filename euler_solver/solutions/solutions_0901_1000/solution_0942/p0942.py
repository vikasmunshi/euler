#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 942: Mersenne's Square Root.

Problem Statement:
    Given a natural number q, let p = 2^q - 1 be the q-th Mersenne number.

    Let R(q) be the minimal square root of q modulo p, if one exists. In other words,
    R(q) is the smallest positive integer x such that x^2 - q is divisible by p.

    For example, R(5) = 6 and R(17) = 47569.

    Find R(74207281). Give your answer modulo 10^9 + 7.

    Note: 2^74207281 - 1 is prime.

URL: https://projecteuler.net/problem=942
"""
from typing import Any

euler_problem: int = 942
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'q': 5}, 'answer': None},
    {'category': 'dev', 'input': {'q': 17}, 'answer': None},
    {'category': 'main', 'input': {'q': 74207281}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
