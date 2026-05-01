#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 311: Biclinic Integral Quadrilaterals.

Problem Statement:
    ABCD is a convex integer sided quadrilateral with 1 <= AB < BC < CD < AD.
    BD has integer length. O is the midpoint of BD. AO has integer length.
    We'll call ABCD a biclinic integral quadrilateral if AO = CO <= BO = DO.
    For example: AB = 19, BC = 29, CD = 37, AD = 43, BD = 48 and AO = CO = 23.
    Let B(N) be the number of distinct biclinic integral quadrilaterals ABCD that
    satisfy AB^2 + BC^2 + CD^2 + AD^2 <= N. We can verify that B(10000) = 49
    and B(1000000) = 38239.
    Find B(10,000,000,000).

URL: https://projecteuler.net/problem=311
"""
from typing import Any

euler_problem: int = 311
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'MbB0rr/ensL0n5AvI0YV5A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
