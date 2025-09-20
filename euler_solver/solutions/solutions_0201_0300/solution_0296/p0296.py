#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 296: Angular Bisector and Tangent.

Problem Statement:
    Given is an integer sided triangle ABC with BC <= AC <= AB.
    k is the angular bisector of angle ACB.
    m is the tangent at C to the circumscribed circle of ABC.
    n is a line parallel to m through B.
    The intersection of n and k is called E.

    How many triangles ABC with a perimeter not exceeding 100000 exist such that
    BE has integral length?

URL: https://projecteuler.net/problem=296
"""
from typing import Any

euler_problem: int = 296
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
