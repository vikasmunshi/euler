#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 372: Pencils of Rays.

Problem Statement:
    Let R(M, N) be the number of lattice points (x, y) which satisfy
    M < x <= N, M < y <= N and floor(y^2 / x^2) is odd.
    We can verify that R(0, 100) = 3019 and R(100, 10000) = 29750422.
    Find R(2*10^6, 10^9).

    Note: floor(x) represents the floor function.

Solution Approach:
    Count lattice pairs (x,y) by fixing x and counting y in (M, N] for which
    floor((y/x)^2) is an odd integer. For a given odd k >= 0, y must lie in
    (sqrt(k)*x, sqrt(k+1)*x]. Sum integer counts over relevant k.
    Use grouping and integer-interval arithmetic to avoid per-point checks.
    Exploit monotonicity of sqrt boundaries; apply floor-sum techniques and
    range grouping to reduce complexity (aim for sublinear in N, using O(s)
    block decomposition where s ~ N^(1/2) or N^(2/3) depending on grouping).
    Careful handling of bounds M and N and tight integer arithmetic is required.

Answer: ...
URL: https://projecteuler.net/problem=372
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 372
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_limit': 0, 'max_limit': 100}},
    {'category': 'main', 'input': {'min_limit': 2000000, 'max_limit': 1000000000}},
    {'category': 'extra', 'input': {'min_limit': 100, 'max_limit': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pencils_of_rays_p0372_s0(*, min_limit: int, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))