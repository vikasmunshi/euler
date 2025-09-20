#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 292: Pythagorean Polygons.

Problem Statement:
    We shall define a pythagorean polygon to be a convex polygon with the
    following properties:
        - there are at least three vertices,
        - no three vertices are aligned,
        - each vertex has integer coordinates,
        - each edge has integer length.

    For a given integer n, define P(n) as the number of distinct pythagorean
    polygons for which the perimeter is <= n.
    Pythagorean polygons should be considered distinct as long as none is a
    translation of another.

    You are given that P(4) = 1, P(30) = 3655 and P(60) = 891045.
    Find P(120).

URL: https://projecteuler.net/problem=292
"""
from typing import Any

euler_problem: int = 292
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 120}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 240}, 'answer': None},
]
encrypted: str = (
    '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'
    '6K0/LfIx1nkK1MDdLNnJa2i3e9Lr3gdD'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
