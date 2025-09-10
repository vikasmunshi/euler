#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 222: Sphere Packing.

Problem Statement:
    What is the length of the shortest pipe, of internal radius 50 mm, that can
    fully contain 21 balls of radii 30 mm, 31 mm, ..., 50 mm?

    Give your answer in micrometres (10^-6 m) rounded to the nearest integer.

Solution Approach:
    Use geometric constraints for spheres inside a cylinder: each sphere center
    must lie within the pipe and spheres may touch the wall. For any pair of
    spheres derive the minimal possible axial separation given the cylinder
    radius and their radii (analytical geometry). The pipe length equals the
    span of centers plus end caps given radii.

    The combinatorial task is to order the 21 spheres to minimize total axial
    length. Use optimization over permutations with strong pruning: compute
    pairwise minimal axial separations, apply branch-and-bound or a bitmask
    DP with lower bounds to search the 21! space efficiently. Expect heavy
    computation; aim for O(2^n * n) DP or well-pruned backtracking.

Answer: ...
URL: https://projecteuler.net/problem=222
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 222
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sphere_packing_p0222_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))