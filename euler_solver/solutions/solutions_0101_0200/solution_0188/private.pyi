#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 188: Hyperexponentiation.

Problem Statement:
    The hyperexponentiation or tetration of a number a by a positive integer b,
    denoted by a ↑↑ b or ^b a, is recursively defined by:

    a ↑↑ 1 = a
    a ↑↑ (k+1) = a^(a ↑↑ k)

    Thus we have e.g. 3 ↑↑ 2 = 3^3 = 27, hence 3 ↑↑ 3 = 3^27 = 7625597484987.
    3 ↑↑ 4 is roughly 10^ (3.6383346400240996 × 10^12).

    Find the last 8 digits of 1777 ↑↑ 1855.

Solution Approach:
    Use modular arithmetic and fast modular exponentiation to evaluate the tower
    modulo 10^8. Reduce exponents using Euler's theorem / Carmichael function
    (lambda) and a totient/lambda chain so very large exponents are reduced.
    Handle cases where exponent < modulus by avoiding reduction, and add the
    modulus when reducing to preserve equivalence. Time: polylog in modulus;
    Space: O(depth of totient chain) which is small for 10^8.

Answer: ...
URL: https://projecteuler.net/problem=188
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 188
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'base': 3, 'height': 3, 'mod_digits': 8}},
    {'category': 'main', 'input': {'base': 1777, 'height': 1855, 'mod_digits': 8}},
    {'category': 'extra', 'input': {'base': 2, 'height': 10000, 'mod_digits': 8}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_hyperexponentiation_p0188_s0(*, base: int, height: int, mod_digits: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))