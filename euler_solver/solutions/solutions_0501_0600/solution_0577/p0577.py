#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 577: Counting Hexagons.

Problem Statement:
    An equilateral triangle with integer side length n >= 3 is divided into n^2
    equilateral triangles with side length 1 as shown in the diagram below.
    The vertices of these triangles constitute a triangular lattice with
    (n+1)(n+2)/2 lattice points.

    Let H(n) be the number of all regular hexagons that can be found by connecting
    6 of these points.

    For example, H(3)=1, H(6)=12 and H(20)=966.

    Find the sum from n=3 to 12345 of H(n).

URL: https://projecteuler.net/problem=577
"""
from typing import Any

euler_problem: int = 577
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 12345}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
