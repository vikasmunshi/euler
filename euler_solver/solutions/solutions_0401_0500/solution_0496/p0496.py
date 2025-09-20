#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 496: Incenter and Circumcenter of Triangle.

Problem Statement:
    Given an integer sided triangle ABC:
    Let I be the incenter of ABC.
    Let D be the intersection between the line AI and the circumcircle of ABC (A != D).

    We define F(L) as the sum of BC for the triangles ABC that satisfy AC = DI and BC <= L.

    For example, F(15) = 45 because the triangles ABC with (BC, AC, AB) = (6,4,5), (12,8,10),
    (12,9,7), (15,9,16) satisfy the conditions.

    Find F(10^9).

URL: https://projecteuler.net/problem=496
"""
from typing import Any

euler_problem: int = 496
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 15}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'B33zRSZHC7xiYgvkp8LzQ43F1kEB8AfX'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
