#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 222: Sphere Packing.

Problem Statement:
    What is the length of the shortest pipe, of internal radius 50 mm, that can
    fully contain 21 balls of radii 30 mm, 31 mm, ..., 50 mm?

    Give your answer in micrometres (10^-6 m) rounded to the nearest integer.

URL: https://projecteuler.net/problem=222
"""
from typing import Any

euler_problem: int = 222
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
