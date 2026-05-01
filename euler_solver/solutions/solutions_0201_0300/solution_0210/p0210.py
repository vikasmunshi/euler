#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 210: Obtuse Angled Triangles.

Problem Statement:
    Consider the set S(r) of points (x,y) with integer coordinates satisfying
    |x| + |y| <= r.
    Let O be the point (0,0) and C the point (r/4,r/4).
    Let N(r) be the number of points B in S(r) so that the triangle OBC has
    an obtuse angle, i.e. the largest angle alpha satisfies 90° < alpha < 180°.
    So, for example, N(4)=24 and N(8)=100.
    What is N(1,000,000,000)?

URL: https://projecteuler.net/problem=210
"""
from typing import Any

euler_problem: int = 210
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
