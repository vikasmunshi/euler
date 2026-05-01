#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 351: Hexagonal Orchards.

Problem Statement:
    A hexagonal orchard of order n is a triangular lattice made up of points
    within a regular hexagon with side n. The following is an example of a
    hexagonal orchard of order 5:

    Highlighted in green are the points which are hidden from the center by a
    point closer to it. It can be seen that for a hexagonal orchard of order 5,
    30 points are hidden from the center.

    Let H(n) be the number of points hidden from the center in a hexagonal
    orchard of order n.

    H(5) = 30. H(10) = 138. H(1,000) = 1177848.

    Find H(100,000,000).

URL: https://projecteuler.net/problem=351
"""
from typing import Any

euler_problem: int = 351
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
