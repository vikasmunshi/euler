#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 864: Square + 1 = Squarefree.

Problem Statement:
    Let C(n) be the number of squarefree integers of the form x^2 + 1 such that
    1 <= x <= n.

    For example, C(10) = 9 and C(1000) = 895.

    Find C(123567101113).

URL: https://projecteuler.net/problem=864
"""
from typing import Any

euler_problem: int = 864
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 123567101113}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
