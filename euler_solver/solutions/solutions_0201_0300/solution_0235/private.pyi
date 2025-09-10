#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 235: An Arithmetic Geometric Sequence.

Problem Statement:
    Given is the arithmetic-geometric sequence u(k) = (900-3k)r^{k - 1}.
    Let s(n) = sum_{k = 1}^n u(k).

    Find the value of r for which s(5000) = -600,000,000,000.

    Give your answer rounded to 12 places behind the decimal point.

Solution Approach:
    Derive a closed form for S(n) = sum_{k=1}^n (900 - 3k) r^{k-1} by combining the
    geometric series sum r^{k-1} and the weighted sum sum k r^{k-1}. Use known
    identities (or differentiate the geometric series) to get O(1) evaluation.
    Reduce the problem to solving f(r) = S(5000) - target = 0 for r (real root).
    Use a robust high-precision root-finding method (bisection/Newton with
    safeguards) and stable formula evaluation for r near 1. Expect fast runtime
    (constant-time evaluations, few dozen iterations) and low memory use.

Answer: ...
URL: https://projecteuler.net/problem=235
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 235
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_an_arithmetic_geometric_sequence_p0235_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))