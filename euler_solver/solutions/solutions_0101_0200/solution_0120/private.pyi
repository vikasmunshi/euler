#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 120: Square Remainders.

Problem Statement:
    Let r be the remainder when (a - 1)^n + (a + 1)^n is divided by a^2.
    For example, if a = 7 and n = 3, then r = 42: 6^3 + 8^3 = 728 = 42 (mod 49).
    And as n varies, so too will r, but for a = 7 it turns out that r_max = 42.
    For 3 <= a <= 1000, find the sum of r_max.

Solution Approach:
    Use the binomial theorem to expand (a-1)^n and (a+1)^n and reduce modulo a^2.
    Analyze parity of n to see which binomial terms survive modulo a^2.
    Derive a closed-form expression for r (or its behavior) and the maximal r per a.
    Compute r_max for each a from 3 to max_limit and sum them. O(max_limit) time.

Answer: ...
URL: https://projecteuler.net/problem=120
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 120
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000}},
    {'category': 'extra', 'input': {'max_limit': 5000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_square_remainders_p0120_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
