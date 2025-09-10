#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 370: Geometric Triangles.

Problem Statement:
    Let us define a geometric triangle as an integer sided triangle with sides
    a <= b <= c so that its sides form a geometric progression, i.e. b^2 = a*c

    An example of such a geometric triangle is the triangle with sides
    a = 144, b = 156 and c = 169.

    There are 861805 geometric triangles with perimeter <= 10^6.

    How many geometric triangles exist with perimeter <= 2.5*10^13?

Solution Approach:
    Parametrise integer geometric progressions by primitive ratios x <= y with
    gcd(x,y)=1 so that sides are proportional to x^2, x*y, y^2 and scaled by
    an integer k. The base perimeter is p0 = x^2 + x*y + y^2; valid k satisfy
    k * p0 <= max_limit and the triangle inequality reduces to x^2 + x*y > y^2.
    Count primitive pairs (x,y) meeting the inequality and sum floor(max_limit/p0).
    Key ideas: number theory, coprime enumeration, bounding y by sqrt(max_limit).
    Expected complexity: roughly O(sqrt(max_limit)) work with careful enumeration.

Answer: ...
URL: https://projecteuler.net/problem=370
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 370
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 25000000000000}},
    {'category': 'extra', 'input': {'max_limit': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_geometric_triangles_p0370_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))