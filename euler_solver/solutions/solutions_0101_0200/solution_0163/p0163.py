#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 163: Cross-hatched Triangles.

Problem Statement:
    Consider an equilateral triangle in which straight lines are drawn from
    each vertex to the middle of the opposite side, as in the size 1 sketch.
    Sixteen triangles of different shape, size, orientation or location can
    be observed in that triangle. Using size 1 triangles as building blocks,
    larger triangles can be formed (for example size 2 shown). The size 2
    triangle contains 104 triangles of differing shape, size, orientation or
    location.

    A size 2 triangle contains 4 size 1 building blocks. A size 3 triangle
    contains 9 size 1 blocks, and in general a size n triangle contains n^2
    size 1 building blocks.

    If T(n) denotes the number of triangles present in a triangle of size n,
    then
        T(1) = 16
        T(2) = 104

    Find T(36).

URL: https://projecteuler.net/problem=163
"""
from typing import Any

euler_problem: int = 163
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 36}, 'answer': None},
    {'category': 'extra', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    '0kcFrXAb2oFrbWN6UYiTViwcUYrKrfi/'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
