#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 919: Fortunate Triangles.

Problem Statement:
    We call a triangle fortunate if it has integral sides and at least one of its
    vertices has the property that the distance from it to the triangle's orthocentre
    is exactly half the distance from the same vertex to the triangle's circumcentre.

    Triangle ABC with sides (6,7,8) is an example of a fortunate triangle. The distance
    from vertex C to the circumcentre O is approximately 4.131182, while the distance
    from C to the orthocentre H is half that, approximately 2.065591.

    Define S(P) to be the sum of a+b+c over all fortunate triangles with sides a ≤ b ≤ c
    and perimeter not exceeding P.

    For example, S(10) = 24, arising from three triangles with sides (1,2,2), (2,3,4),
    and (2,4,4). Also, S(100) = 3331.

    Find S(10^7).

URL: https://projecteuler.net/problem=919
"""
from typing import Any

euler_problem: int = 919
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
