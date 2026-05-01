#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 233: Lattice Points on a Circle.

Problem Statement:
    Let f(N) be the number of points with integer coordinates that are on a
    circle passing through (0,0), (N,0), (0,N), and (N,N).

    It can be shown that f(10000) = 36.

    What is the sum of all positive integers N ≤ 10^11 such that f(N) = 420?

URL: https://projecteuler.net/problem=233
"""
from typing import Any

euler_problem: int = 233
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'F5fKhy3fLtAA3Gnhni+twiUviqk='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
