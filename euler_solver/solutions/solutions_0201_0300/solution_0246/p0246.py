#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 246: Tangents to an Ellipse.

Problem Statement:
    A definition for an ellipse is:
    Given a circle c with centre M and radius r and a point G such that
    d(G,M) < r, the locus of the points that are equidistant from c and G
    form an ellipse.

    Given are the points M(-2000,1500) and G(8000,1500).
    Given is also the circle c with centre M and radius 15000.
    The locus of the points that are equidistant from G and c form an
    ellipse e. From a point P outside e the two tangents t1 and t2 to
    the ellipse are drawn. Let the points where t1 and t2 touch the
    ellipse be R and S.

    For how many lattice points P is angle RPS greater than 45 degrees?

URL: https://projecteuler.net/problem=246
"""
from typing import Any

euler_problem: int = 246
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '86jLjqBUCWpTJ3EEL8/4CMxP/kzTjUnF'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
