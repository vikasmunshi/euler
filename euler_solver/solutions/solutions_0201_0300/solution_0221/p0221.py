#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 221: Alexandrian Integers.

Problem Statement:
    We shall call a positive integer A an "Alexandrian integer", if there exist
    integers p, q, r such that:

    A = p * q * r
    and
    1/A = 1/p + 1/q + 1/r.

    For example, 630 is an Alexandrian integer (p = 5, q = -7, r = -18).
    In fact, 630 is the 6th Alexandrian integer, the first 6 being:
    6, 42, 120, 156, 420, 630.

    Find the 150000th Alexandrian integer.

URL: https://projecteuler.net/problem=221
"""
from typing import Any

euler_problem: int = 221
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 150000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
    '+wgltZkoZJcwXye9bL+Ezw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
