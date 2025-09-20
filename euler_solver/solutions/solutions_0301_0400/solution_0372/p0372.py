#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 372: Pencils of Rays.

Problem Statement:
    Let R(M, N) be the number of lattice points (x, y) which satisfy
    M < x <= N, M < y <= N and floor(y^2 / x^2) is odd.
    We can verify that R(0, 100) = 3019 and R(100, 10000) = 29750422.
    Find R(2*10^6, 10^9).

    Note: floor(x) represents the floor function.

URL: https://projecteuler.net/problem=372
"""
from typing import Any

euler_problem: int = 372
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_limit': 0, 'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'min_limit': 2000000, 'max_limit': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'min_limit': 100, 'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    '1LQuUAacvqg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
