#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 279: Triangles with Integral Sides and an Integral Angle.

Problem Statement:
    How many triangles are there with integral sides, at least one integral angle
    (measured in degrees), and a perimeter that does not exceed 10^8?

URL: https://projecteuler.net/problem=279
"""
from typing import Any

euler_problem: int = 279
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'exxogkERlFVdv/5I'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
