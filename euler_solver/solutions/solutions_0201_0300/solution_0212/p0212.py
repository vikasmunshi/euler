#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 212: Combined Volume of Cuboids.

Problem Statement:
    An axis-aligned cuboid, specified by parameters {(x0, y0, z0), (dx, dy, dz)},
    consists of all points (X, Y, Z) such that x0 <= X <= x0 + dx, y0 <= Y <=
    y0 + dy and z0 <= Z <= z0 + dz. The volume of the cuboid is the product
    dx * dy * dz. The combined volume of a collection of cuboids is the volume
    of their union and will be less than the sum of the individual volumes if
    any cuboids overlap.

    Let C1, ..., C50000 be a collection of 50000 axis-aligned cuboids such that
    Cn has parameters:

    x0 = S_{6n - 5} mod 10000
    y0 = S_{6n - 4} mod 10000
    z0 = S_{6n - 3} mod 10000
    dx = 1 + (S_{6n - 2} mod 399)
    dy = 1 + (S_{6n - 1} mod 399)
    dz = 1 + (S_{6n}     mod 399)

    where S1, ..., S300000 come from the "Lagged Fibonacci Generator":

    For 1 <= k <= 55, S_k = [100003 - 200003*k + 300007*k^3] mod 1000000.
    For 56 <= k, S_k = [S_{k-24} + S_{k-55}] mod 1000000.

    Thus, C1 has parameters {(7,53,183),(94,369,56)}, C2 has parameters
    {(2383,3563,5079),(42,212,344)}, and so on.

    The combined volume of the first 100 cuboids, C1, ..., C100, is 723581599.

    What is the combined volume of all 50000 cuboids, C1, ..., C50000?

URL: https://projecteuler.net/problem=212
"""
from typing import Any

euler_problem: int = 212
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_cuboids': 100}, 'answer': None},
    {'category': 'main', 'input': {'num_cuboids': 50000}, 'answer': None},
    {'category': 'extra', 'input': {'num_cuboids': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
