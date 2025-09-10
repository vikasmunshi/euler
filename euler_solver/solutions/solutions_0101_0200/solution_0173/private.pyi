#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 173: Hollow Square Laminae I.

Problem Statement:
    We shall define a square lamina to be a square outline with a square "hole"
    so that the shape possesses vertical and horizontal symmetry. For example,
    using exactly thirty-two square tiles we can form two different square
    laminae.

    With one-hundred tiles, and not necessarily using all of the tiles at one
    time, it is possible to form forty-one different square laminae.

    Using up to one million tiles how many different square laminae can be
    formed?

Solution Approach:
    Count pairs of outer side n and inner side m (n>m, same parity) where tiles
    used = n^2 - m^2 = 4*k*(n-k) with k = (n-m)/2 >= 1. Iterate thickness k
    and compute how many outer sizes n satisfy 4*k*(n-k) <= max_limit and n>2k.
    This yields an O(max_limit) loop (k up to max_limit//4) with O(1) work each.
    Use integer arithmetic only; space O(1).

Answer: ...
URL: https://projecteuler.net/problem=173
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 173
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 32}},
    {'category': 'main', 'input': {'max_limit': 1000000}},
    {'category': 'extra', 'input': {'max_limit': 2000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_hollow_square_laminae_i_p0173_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))