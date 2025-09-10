#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 625: Gcd Sum.

Problem Statement:
    G(N) = sum from j=1 to N of sum from i=1 to j of gcd(i, j).
    You are given: G(10) = 122.

    Find G(10^11). Give your answer modulo 998244353.

Solution Approach:
    Use number theory properties of gcd sums and possibly convolution or divisor
    summation formulas. Fast computation through multiplicative functions and
    modular arithmetic is key. Expect O(N^0.5) or better via analytic or sieve methods.

Answer: ...
URL: https://projecteuler.net/problem=625
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 625
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 100000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_gcd_sum_p0625_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))