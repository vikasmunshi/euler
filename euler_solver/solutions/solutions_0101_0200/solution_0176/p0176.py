#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 176: Common Cathetus Right-angled Triangles.

Problem Statement:
    The four right-angled triangles with sides (9,12,15), (12,16,20), (5,12,13)
    and (12,35,37) all have one of the shorter sides (catheti) equal to 12. It
    can be shown that no other integer sided right-angled triangle exists with
    one of the catheti equal to 12.

    Find the smallest integer that can be the length of a cathetus of exactly
    47547 different integer sided right-angled triangles.

URL: https://projecteuler.net/problem=176
"""
from typing import Any

euler_problem: int = 176
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target_count': 4}, 'answer': None},
    {'category': 'main', 'input': {'target_count': 47547}, 'answer': None},
    {'category': 'extra', 'input': {'target_count': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
