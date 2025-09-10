#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 390: Triangles with Non Rational Sides and Integral Area.

Problem Statement:
    Consider the triangle with sides sqrt(5), sqrt(65) and sqrt(68). It can be
    shown that this triangle has area 9.

    S(n) is the sum of the areas of all triangles with sides sqrt(1+b^2),
    sqrt(1+c^2) and sqrt(b^2+c^2) (for positive integers b and c) that have an
    integral area not exceeding n.

    The example triangle has b = 2 and c = 8.

    S(10^6) = 18018206.

    Find S(10^10).

Solution Approach:
    Use Heron's formula and algebraic simplification to derive a Diophantine
    condition on integer parameters b and c that yields integral area.
    Parameterize and factor the resulting expressions and count solutions by
    enumerating divisors or using multiplicative properties to avoid a naive
    double loop. Expected to rely on number theory and efficient divisor
    enumeration to run well for n = 10^10 (subquadratic with optimizations).

Answer: ...
URL: https://projecteuler.net/problem=390
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 390
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1000000}},
    {'category': 'main', 'input': {'n': 10000000000}},
    {'category': 'extra', 'input': {'n': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_triangles_with_non_rational_sides_and_integral_area_p0390_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))