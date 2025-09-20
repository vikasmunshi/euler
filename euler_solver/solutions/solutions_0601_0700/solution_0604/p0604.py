#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 604: Convex Path in Square.

Problem Statement:
    Let F(N) be the maximum number of lattice points in an axis-aligned N by N square
    that the graph of a single strictly convex increasing function can pass through.

    You are given that F(1) = 2, F(3) = 3, F(9) = 6, F(11) = 7, F(100) = 30 and
    F(50000) = 1898.
    Below is the graph of a function reaching the maximum 3 for N=3:

    Find F(10^18).

URL: https://projecteuler.net/problem=604
"""
from typing import Any

euler_problem: int = 604
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '4iZIdPcVtio='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
