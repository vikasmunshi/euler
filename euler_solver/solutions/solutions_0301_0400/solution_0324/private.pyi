#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 324: Building a Tower.

Problem Statement:
    Let f(n) represent the number of ways one can fill a 3 x 3 x n tower with
    blocks of 2 x 1 x 1.
    You're allowed to rotate the blocks in any way you like; however, rotations,
    reflections etc of the tower itself are counted as distinct.

    For example (with q = 100000007):
    f(2) = 229,
    f(4) = 117805,
    f(10) mod q = 96149360,
    f(10^3) mod q = 24806056,
    f(10^6) mod q = 30808124.

    Find f(10^10000) mod 100000007.

Solution Approach:
    Model tilings as transitions between consecutive 3 x 3 cross-sections using
    a transfer matrix. Represent each cross-section filling as a bitmask/state
    and enumerate legal placements of 2x1x1 blocks to build the adjacency.
    Use fast matrix exponentiation (binary exponentiation) of the transfer
    matrix to the huge power 10^10000 modulo q. Work entirely in modular
    arithmetic and exploit state compression and sparsity to reduce cost.
    Expected complexity: O(m^3 log N) with naive matrix mult (m = state count),
    or lower with sparse/optimized multiplication and state pruning.

Answer: ...
URL: https://projecteuler.net/problem=324
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 324
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'power': 1, 'mod': 100000007}},
    {'category': 'main', 'input': {'power': 10000, 'mod': 100000007}},
    {'category': 'extra', 'input': {'power': 100000, 'mod': 100000007}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_building_a_tower_p0324_s0(*, power: int, mod: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))