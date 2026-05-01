#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 449: Chocolate Covered Candy.

Problem Statement:
    Phil the confectioner is making a new batch of chocolate covered candy.
    Each candy centre is shaped like an ellipsoid of revolution defined by the
    equation:
        b^2 x^2 + b^2 y^2 + a^2 z^2 = a^2 b^2.

    Phil wants to know how much chocolate is needed to cover one candy centre
    with a uniform coat of chocolate one millimeter thick.

    If a = 1 mm and b = 1 mm, the amount of chocolate required is (28/3) * pi
    mm^3.

    If a = 2 mm and b = 1 mm, the amount of chocolate required is
    approximately 60.35475635 mm^3.

    Find the amount of chocolate in mm^3 required if a = 3 mm and b = 1 mm.
    Give your answer as the number rounded to 8 decimal places behind the
    decimal point.

URL: https://projecteuler.net/problem=449
"""
from typing import Any

euler_problem: int = 449
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'a': 1, 'b': 1}, 'answer': None},
    {'category': 'main', 'input': {'a': 3, 'b': 1}, 'answer': None},
    {'category': 'extra', 'input': {'a': 10, 'b': 5}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
