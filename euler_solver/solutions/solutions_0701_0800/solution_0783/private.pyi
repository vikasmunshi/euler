#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 783: Urns.

Problem Statement:
    Given n and k two positive integers we begin with an urn that contains kn
    white balls. We then proceed through n turns where on each turn k black balls
    are added to the urn and then 2k random balls are removed from the urn.

    We let B_t(n,k) be the number of black balls that are removed on turn t.

    Further define E(n,k) as the expectation of the sum from t=1 to n of
    B_t(n,k)^2.

    You are given E(2,2) = 9.6.

    Find E(10^6,10). Round your answer to the nearest whole number.

Solution Approach:
    Use probability and expectation theory involving the hypergeometric
    distribution to model the number of black balls removed each turn.
    Employ recurrence relations or dynamic programming to compute expected
    squared values efficiently. Numerical methods or approximations might be
    required for large n and k, focusing on O(n) or better complexity.

Answer: ...
URL: https://projecteuler.net/problem=783
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 783
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2, 'k': 2}},
    {'category': 'main', 'input': {'n': 1000000, 'k': 10}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_urns_p0783_s0(*, n: int, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))