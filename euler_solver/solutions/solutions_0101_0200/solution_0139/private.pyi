#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 139: Pythagorean Tiles.

Problem Statement:
    Let (a, b, c) represent the three sides of a right angle triangle
    with integral length sides. It is possible to place four such triangles
    together to form a square with side length c.

    For example, (3, 4, 5) triangles can be placed together to form a 5 by 5
    square with a 1 by 1 hole in the middle, and the 5 by 5 square can be
    tiled with twenty-five 1 by 1 squares.

    However, if (5, 12, 13) triangles were used then the hole would measure
    7 by 7 and these could not be used to tile the 13 by 13 square.

    Given that the perimeter of the right triangle is less than
    one-hundred million, how many Pythagorean triangles would allow such a
    tiling to take place?

Solution Approach:
    Use the standard parameterization of Pythagorean triples: for coprime
    integers m>n of opposite parity, a = m^2 - n^2, b = 2mn, c = m^2 + n^2,
    and include scaled multiples k*(a,b,c). Derive the necessary arithmetic
    condition on a,b,c that allows the c-by-c square formed by four copies
    to be tiled (expressible in terms of divisibility/commensurability of
    the inner hole). Enumerate primitive (m,n) pairs with c up to the limit,
    extend by multiples while perimeter < limit, and count valid triples.
    Complexity: roughly proportional to the number of generated triples;
    expected to run in near-linear time in the number of valid c values.

Answer: ...
URL: https://projecteuler.net/problem=139
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 139
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_perimeter': 100}},
    {'category': 'main', 'input': {'max_perimeter': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pythagorean_tiles_p0139_s0(*, max_perimeter: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))