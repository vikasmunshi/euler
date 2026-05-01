#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 332: Spherical Triangles.

Problem Statement:
    A spherical triangle is a figure formed on the surface of a sphere by three
    great circular arcs intersecting pairwise in three vertices.

    Let C(r) be the sphere with the centre (0,0,0) and radius r.
    Let Z(r) be the set of points on the surface of C(r) with integer coordinates.
    Let T(r) be the set of spherical triangles with vertices in Z(r).
    Degenerate spherical triangles, formed by three points on the same great arc,
    are not included in T(r).
    Let A(r) be the area of the smallest spherical triangle in T(r).

    For example A(14) is 3.294040 rounded to six decimal places.

    Find sum_{r=1}^{50} A(r). Give your answer rounded to six decimal places.

URL: https://projecteuler.net/problem=332
"""
from typing import Any

euler_problem: int = 332
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 50}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'fvVUIlxCbPLrhjOnV/rCufQja3rZItCHl3j7Uw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
