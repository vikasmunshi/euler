#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 128: Hexagonal Tile Differences.

Problem Statement:
    A hexagonal tile with number 1 is surrounded by a ring of six hexagonal tiles,
    starting at "12 o'clock" and numbering the tiles 2 to 7 in an anti-clockwise
    direction.
    New rings are added in the same fashion, with the next rings being numbered
    8 to 19, 20 to 37, 38 to 61, and so on.
    By finding the difference between tile n and each of its six neighbours we
    shall define PD(n) to be the number of those differences which are prime.
    For example, working clockwise around tile 8 the differences are 12, 29, 11,
    6, 1, and 13. So PD(8) = 3.
    In the same way, the differences around tile 17 are 1, 17, 16, 1, 11, and 10,
    hence PD(17) = 2.
    It can be shown that the maximum value of PD(n) is 3.
    If all of the tiles for which PD(n) = 3 are listed in ascending order to
    form a sequence, the 10th tile would be 271.
    Find the 2000th tile in this sequence.

Solution Approach:
    Analyze the hexagonal spiral ring structure and derive closed-form formulas
    for tile indices on ring k and their neighbour offsets. Restrict attention
    to the positions that can yield PD(n) = 3 (these occur at predictable ring
    positions near corners/edges).
    For each candidate tile compute the six neighbour differences and test
    primality using a deterministic Miller–Rabin for 64-bit integers (or a fast
    deterministic variant). Iterate rings until the required count is found.
    Complexity: O(m * log^c N) where m is required count (2000) and N is tile
    magnitude; memory O(1).

Answer: ...
URL: https://projecteuler.net/problem=128
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 128
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 2000}},
    {'category': 'extra', 'input': {'n': 5000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_hexagonal_tile_differences_p0128_s0(*, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))