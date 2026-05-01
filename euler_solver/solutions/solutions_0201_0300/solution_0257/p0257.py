#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 257: Angular Bisectors.

Problem Statement:
    Given is an integer sided triangle ABC with sides a <= b <= c. (AB = c,
    BC = a and AC = b.)
    The angular bisectors of the triangle intersect the sides at points E, F
    and G.
    The segments EF, EG and FG partition the triangle ABC into four smaller
    triangles: AEG, BFE, CGF and EFG.
    It can be proven that for each of these four triangles the ratio
    area(ABC)/area(subtriangle) is rational. However, there exist triangles
    for which some or all of these ratios are integral.
    How many triangles ABC with perimeter <= 100000000 exist so that the
    ratio area(ABC)/area(AEG) is integral?

URL: https://projecteuler.net/problem=257
"""
from typing import Any

euler_problem: int = 257
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
