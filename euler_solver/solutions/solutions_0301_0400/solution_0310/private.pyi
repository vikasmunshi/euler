#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 310: Nim Square.

Problem Statement:
    Alice and Bob play the game Nim Square.
    Nim Square is like ordinary three-heap normal-play Nim, but players may only
    remove a square number of stones from a heap.
    The number of stones in the three heaps is represented by the ordered triple
    (a, b, c). If 0 <= a <= b <= c <= 29 then the number of losing positions for
    the next player is 1160.
    Find the number of losing positions for the next player if 0 <= a <= b <= c
    <= 100000.

Solution Approach:
    Use Sprague–Grundy theory: compute Grundy g(n) for a single heap where
    g(n) = mex{ g(n - s^2) : s^2 <= n }.
    Precompute g(n) for n = 0..max_limit in O(max_limit * sqrt(max_limit)) time.
    Count ordered nondecreasing triples (a <= b <= c) with g(a)^g(b)^g(c) == 0.
    Aggregate counts by Grundy value and use combinatorics over the small Grundy
    value range to enumerate valid triples efficiently.
    Expected complexity: O(max_limit * sqrt(max_limit) + G^2) time, O(max_limit) space.

Answer: ...
URL: https://projecteuler.net/problem=310
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 310
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 29}},
    {'category': 'main', 'input': {'max_limit': 100000}},
    {'category': 'extra', 'input': {'max_limit': 200000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_nim_square_p0310_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))