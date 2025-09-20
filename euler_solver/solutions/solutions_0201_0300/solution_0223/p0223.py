#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 223: Almost Right-angled Triangles I.

Problem Statement:
    Let us call an integer sided triangle with sides a <= b <= c barely acute if
    the sides satisfy a^2 + b^2 = c^2 + 1.

    How many barely acute triangles are there with perimeter <= 25,000,000?

URL: https://projecteuler.net/problem=223
"""
from typing import Any

euler_problem: int = 223
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 25000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'rbgubVGXY7MVF/RCFN53/g=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
