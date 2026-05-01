#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 600: Integer Sided Equiangular Hexagons.

Problem Statement:
    Let H(n) be the number of distinct integer sided equiangular convex hexagons
    with perimeter not exceeding n.
    Hexagons are distinct if and only if they are not congruent.

    You are given H(6) = 1, H(12) = 10, H(100) = 31248.
    Find H(55106).

URL: https://projecteuler.net/problem=600
"""
from typing import Any

euler_problem: int = 600
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 12}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 55106}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
