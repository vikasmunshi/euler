#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 360: Scary Sphere.

Problem Statement:
    Given two points (x1, y1, z1) and (x2, y2, z2) in three dimensional space,
    the Manhattan distance between those points is defined as
    |x1 - x2| + |y1 - y2| + |z1 - z2|.

    Let C(r) be a sphere with radius r and center in the origin O(0,0,0).
    Let I(r) be the set of all points with integer coordinates on the
    surface of C(r).
    Let S(r) be the sum of the Manhattan distances of all elements of I(r)
    to the origin O.

    E.g. S(45)=34518.

    Find S(10^10).

Solution Approach:
    Count integer lattice points on the sphere by representing r^2 as x^2+y^2+z^2.
    Use symmetry to group points by absolute coordinate values and permutations.
    For a fixed |x| = a count integer solutions to y^2+z^2 = r^2 - a^2 and use
    formulas for representations as a sum of two squares to get multiplicities.
    Exploit multiplicativity and divisor-sum style formulas after factoring r.
    Time dominated by integer factorization of r; subsequent work is polynomial
    in the number of divisors. Space usage is minimal (O(1) or divisors).

Answer: ...
URL: https://projecteuler.net/problem=360
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 360
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'r': 45}},
    {'category': 'main', 'input': {'r': 10000000000}},
    {'category': 'extra', 'input': {'r': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_scary_sphere_p0360_s0(*, r: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))