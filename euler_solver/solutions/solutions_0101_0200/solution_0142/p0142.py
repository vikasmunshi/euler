#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 142: Perfect Square Collection.

Problem Statement:
    Find the smallest x + y + z with integers x > y > z > 0 such that
    x + y, x - y, x + z, x - z, y + z, y - z are all perfect squares.

URL: https://projecteuler.net/problem=142
"""
from typing import Any

euler_problem: int = 142
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
