#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 442: Eleven-free Integers.

Problem Statement:
    An integer is called eleven-free if its decimal expansion does not contain any
    substring representing a power of 11 except 1.

    For example, 2404 and 13431 are eleven-free, while 911 and 4121331 are not.

    Let E(n) be the nth positive eleven-free integer. For example, E(3) = 3, E(200) =
    213 and E(500000) = 531563.

    Find E(10^18).

URL: https://projecteuler.net/problem=442
"""
from typing import Any

euler_problem: int = 442
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'dev', 'input': {'n': 200}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'yZ1eyt2zeYNDbZV+LMAOseJvm4oacz/Q'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
