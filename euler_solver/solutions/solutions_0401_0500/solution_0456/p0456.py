#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 456: Triangles Containing the Origin II.

Problem Statement:
    Define:
        x_n = (1248^n mod 32323) - 16161
        y_n = (8421^n mod 30103) - 15051
        P_n = {(x_1, y_1), (x_2, y_2), ..., (x_n, y_n)}

    For example, P_8 = {(-14913, -6630), (-10161, 5625), (5226, 11896), (8340, -10778),
    (15852, -5203), (-15165, 11295), (-1427, -14495), (12407, 1060)}.

    Let C(n) be the number of triangles whose vertices are in P_n which contain the origin
    in the interior.

    Examples:
        C(8) = 20
        C(600) = 8950634
        C(40000) = 2666610948988

    Find C(2000000).

URL: https://projecteuler.net/problem=456
"""
from typing import Any

euler_problem: int = 456
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 8}, 'answer': None},
    {'category': 'main', 'input': {'n': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'fWkN8QgtVOfSKyKI'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
