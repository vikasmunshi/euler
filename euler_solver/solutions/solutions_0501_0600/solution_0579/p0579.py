#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 579: Lattice Points in Lattice Cubes.

Problem Statement:
    A lattice cube is a cube in which all vertices have integer coordinates.
    Let C(n) be the number of different lattice cubes in which the coordinates
    of all vertices range between (and including) 0 and n. Two cubes are hereby
    considered different if any of their vertices have different coordinates.

    For example, C(1)=1, C(2)=9, C(4)=100, C(5)=229, C(10)=4469 and C(50)=8154671.

    Different cubes may contain different numbers of lattice points.

    For example, the cube with the vertices
    (0, 0, 0), (3, 0, 0), (0, 3, 0), (0, 0, 3), (0, 3, 3), (3, 0, 3), (3, 3, 0),
    (3, 3, 3) contains 64 lattice points (56 lattice points on the surface including the
    8 vertices and 8 points within the cube).

    In contrast, the cube with the vertices
    (0, 2, 2), (1, 4, 4), (2, 0, 3), (2, 3, 0), (3, 2, 5), (3, 5, 2), (4, 1, 1),
    (5, 3, 3) contains only 40 lattice points (20 points on the surface and 20 points
    within the cube), although both cubes have the same side length 3.

    Let S(n) be the sum of the lattice points contained in the different lattice cubes
    in which the coordinates of all vertices range between (and including) 0 and n.

    For example, S(1)=8, S(2)=91, S(4)=1878, S(5)=5832, S(10)=387003 and S(50)=29948928129.

    Find S(5000) mod 10^9.

URL: https://projecteuler.net/problem=579
"""
from typing import Any

euler_problem: int = 579
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
