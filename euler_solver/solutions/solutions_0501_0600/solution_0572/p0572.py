#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 572: Idempotent Matrices.

Problem Statement:
    A matrix M is called idempotent if M^2 = M.
    Let M be a three by three matrix:
        M = | a  b  c |
            | d  e  f |
            | g  h  i |
    with integer elements.

    Let C(n) be the number of idempotent 3x3 matrices M with integer elements
    such that -n ≤ a,b,c,d,e,f,g,h,i ≤ n.

    Given: C(1) = 164 and C(2) = 848.

    Find C(200).

URL: https://projecteuler.net/problem=572
"""
from typing import Any

euler_problem: int = 572
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 200}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
