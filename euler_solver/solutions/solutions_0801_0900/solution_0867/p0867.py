#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 867: Tiling Dodecagon.

Problem Statement:
    There are 5 ways to tile a regular dodecagon of side 1 with regular polygons of side 1.

    Let T(n) be the number of ways to tile a regular dodecagon of side n with regular polygons
    of side 1. Then T(1) = 5. You are also given T(2) = 48.

    Find T(10). Give your answer modulo 10^9+7.

URL: https://projecteuler.net/problem=867
"""
from typing import Any

euler_problem: int = 867
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 10}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    'PIZRJg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
