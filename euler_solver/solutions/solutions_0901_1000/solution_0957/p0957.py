#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 957: Point Genesis.

Problem Statement:
    There is a plane on which all points are initially white, except three red
    points and two blue points.
    On each day, every line passing through a red point and a blue point is
    constructed. Then every white point, where two different such lines meet,
    turns blue.

    Let g(n) be the maximal possible number of blue points after n days.

    For example, g(1)=8 and g(2)=28.

    Find g(16).

URL: https://projecteuler.net/problem=957
"""
from typing import Any

euler_problem: int = 957
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 16}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
