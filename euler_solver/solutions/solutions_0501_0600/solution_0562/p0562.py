#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 562: Maximal Perimeter.

Problem Statement:
    Construct triangle ABC such that:
        Vertices A, B and C are lattice points inside or on the circle of radius r
        centered at the origin;
        the triangle contains no other lattice point inside or on its edges;
        the perimeter is maximum.

    Let R be the circumradius of triangle ABC and T(r) = R/r.
    For r = 5, one possible triangle has vertices (-4,-3), (4,2) and (1,0) with
    perimeter sqrt(13)+sqrt(34)+sqrt(89) and circumradius R = sqrt(19669/2), so
    T(5) = sqrt(19669/50).
    You are given T(10) approximately 97.26729 and T(100) approximately 9157.64707.

    Find T(10^7). Give your answer rounded to the nearest integer.

URL: https://projecteuler.net/problem=562
"""
from typing import Any

euler_problem: int = 562
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'r': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
